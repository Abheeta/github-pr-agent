from github import Github
from langchain.tools import tool
from urllib.parse import urlparse
import os
import base64
from typing import Optional
import json

def parse_repo_url(repo_url: str) -> tuple[str, str]:
    parsed = urlparse(repo_url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid GitHub repo URL: {repo_url}")
    return parts[0], parts[1]


# @tool
# def fetch_diff(repo_url: str, pr_number: int, github_token: str = None) -> str:
#     """Fetch the code diff of a GitHub PR."""
#     # token = os.getenv("GITHUB_TOKEN")
#     g = Github(github_token) if github_token else Github()

#     owner, repo = parse_repo_url(repo_url)
#     repo_obj = g.get_repo(f"{owner}/{repo}")
#     pr = repo_obj.get_pull(pr_number)

#     diff = ""
#     for file in pr.get_files():
#         diff += f"\n--- {file.filename} ---\n"
#         diff += file.patch or ""
#     return diff

# @tool
# def fetch_diff(repo_url: str, pr_number: int, github_token: Optional[str] = None) -> str:
#     """Fetch the full content and code diff of each file in a GitHub PR."""
#     g = Github(github_token) if github_token else Github()

#     owner, repo = parse_repo_url(repo_url)
#     repo_obj = g.get_repo(f"{owner}/{repo}")
#     pr = repo_obj.get_pull(pr_number)

#     result = []

#     for file in pr.get_files():
#         file_info = {
#             "filename": file.filename,
#             "status": file.status,  # "modified", "added", "removed"
#             "patch": file.patch or ""
#         }

#         if file.status != "added":
#             # Try to get the file content from base branch
#             try:
#                 contents = repo_obj.get_contents(file.filename, ref=pr.base.ref)
#                 file_info["content"] = base64.b64decode(contents.content).decode("utf-8")
#             except Exception as e:
#                 file_info["content"] = None
#                 file_info["error"] = str(e)
#         else:
#             # For newly added files, skip content fetching (patch already has it)
#             file_info["content"] = None

#         result.append(file_info)
#     print("File diff done")
#     return json.dumps(result)

from typing import Optional, Tuple, Dict, List
import json
import base64
from github import Github

@tool
def fetch_diff(repo_url: str, pr_number: int, github_token: Optional[str] = None) -> Tuple[str, str]:
    """
    Fetch the full content and code diff of each file in a GitHub PR.
    
    Returns:
        Tuple[str, str]: (code_diff_json, file_content_json)
            - code_diff_json: JSON string containing diff information for each file
            - file_content_json: JSON string containing original file contents
    """
    g = Github(github_token) if github_token else Github()

    owner, repo = parse_repo_url(repo_url)
    repo_obj = g.get_repo(f"{owner}/{repo}")
    pr = repo_obj.get_pull(pr_number)

    code_diff_data = []
    file_content_data = []

    for file in pr.get_files():
        # Code diff information
        diff_info = {
            "filename": file.filename,
            "status": file.status,  # "modified", "added", "removed"
            "patch": file.patch or "",
            "additions": file.additions,
            "deletions": file.deletions,
            "changes": file.changes
        }
        code_diff_data.append(diff_info)

        # File content information
        content_info = {
            "filename": file.filename,
            "content": None,
            "error": None
        }

        if file.status != "added":
            # Try to get the file content from base branch
            try:
                contents = repo_obj.get_contents(file.filename, ref=pr.base.ref)
                content_info["content"] = base64.b64decode(contents.content).decode("utf-8")
            except Exception as e:
                content_info["error"] = str(e)
        else:
            # For newly added files, we can try to extract content from patch
            # or mark as new file
            content_info["content"] = "NEW_FILE"

        file_content_data.append(content_info)

    print("File diff done")
    
    code_diff_json = json.dumps(code_diff_data, indent=2)
    file_content_json = json.dumps(file_content_data, indent=2)
    
    return code_diff_json, file_content_json

@tool
def analyze_code_diff(code_diff: str, file_content: str) -> dict:
    """Analyze a code diff for style, bugs, performance, and best practices."""
    from langchain_ollama import OllamaLLM 
    from collections import defaultdict
    import json
    import os

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    llm = OllamaLLM(model="codellama:7b", base_url=base_url)

    prompt = f"""
SYSTEM: You are a code review assistant. Analyze the Git diff and return ONLY a JSON array of issues. Do not explain, acknowledge, or provide any other text.

TASK: Identify actual issues introduced by the changes in the diff below.

RULES:
- Only analyze lines with + (additions) and - (deletions)
- Ignore pre-existing code that wasn't changed
- Don't flag intentionally commented-out code as unused
- Focus on problems introduced by the changes

FILE CONTENT BEFORE CHANGES:
{file_content}

GIT DIFF:
{code_diff}

OUTPUT FORMAT - Return ONLY this JSON structure, nothing else:
[
  {{
    "file": "filename",
    "type": "bug|style|performance|best_practice", 
    "line": number,
    "description": "issue description",
    "suggestion": "fix suggestion",
    "critical": true|false
  }}
]

CRITICAL: 
- bug = runtime errors/broken functionality
- performance = significant performance issues
- Return [] if no issues found
- Return *only* raw JSON. Do not wrap the response in triple backticks (```), markdown formatting, or explanations. Just plain JSON, no prefix, no suffix, no code block.
Your response must start with `[` and end with `]`.
"""
    raw_output = llm.invoke(prompt)

    try:
        raw_issues = json.loads(raw_output)
        files_dict = defaultdict(list)
        for issue in raw_issues:
            files_dict[issue["file"]].append({
                "type": issue["type"],
                "line": issue["line"],
                "description": issue["description"],
                "suggestion": issue["suggestion"]
            })

        files = [
            {
                "name": filename,
                "issues": issues
            }
            for filename, issues in files_dict.items()
        ]

        total_issues = len(raw_issues)
        critical_issues = sum(1 for issue in raw_issues if issue.get("critical"))

        summary = {
            "total_files": len(files),
            "total_issues": total_issues,
            "critical_issues": critical_issues
        }

        results = {
            "files": files,
            "summary": summary
        }

        return {"error": None, "raw": results}

    except Exception:
        return {"error": "Failed to parse model response", "raw": raw_output}
