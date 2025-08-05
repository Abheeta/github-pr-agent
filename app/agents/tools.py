from github import Github
from langchain.tools import tool
from urllib.parse import urlparse
import os

def parse_repo_url(repo_url: str) -> tuple[str, str]:
    parsed = urlparse(repo_url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid GitHub repo URL: {repo_url}")
    return parts[0], parts[1]


@tool
def fetch_diff(repo_url: str, pr_number: int) -> str:
    """Fetch the code diff of a GitHub PR."""
    token = os.getenv("GITHUB_TOKEN")
    g = Github(token) if token else Github()

    owner, repo = parse_repo_url(repo_url)
    repo_obj = g.get_repo(f"{owner}/{repo}")
    pr = repo_obj.get_pull(pr_number)

    diff = ""
    for file in pr.get_files():
        diff += f"\n--- {file.filename} ---\n"
        diff += file.patch or ""
    return diff


@tool
def analyze_code_diff(code_diff: str) -> dict:
    """Analyze a code diff for style, bugs, performance, and best practices."""
    from langchain_ollama import OllamaLLM 
    from collections import defaultdict
    import json
    import os

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    llm = OllamaLLM(model="codellama:7b", base_url=base_url)

    prompt = f"""
You are a code review assistant.

Analyze the following code diff and return a JSON list of issues grouped by file. For each issue, include:

- file name
- issue type: one of "style", "bug", "performance", or "best_practice"
- line number
- description
- suggestion
- whether it's critical (true for "bug" or "performance")

Diff:
{code_diff}

Return in this JSON format:

[
  {{
    "file": "",
    "type": "",
    "line": "",
    "description": "",
    "suggestion": "",
    "critical": boolean
  }}
]

Return *only* raw JSON. Do not wrap the response in triple backticks (```), markdown formatting, or explanations. Just plain JSON, no prefix, no suffix, no code block.
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
