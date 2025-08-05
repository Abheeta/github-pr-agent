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

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    llm = OllamaLLM(model="codellama:7b", base_url=base_url)

    prompt = f"""
You are a code review assistant. Analyze the following code diff and return a JSON with:

- Issues of type: "style", "bug", "performance", or "best_practice"
- For each issue: line number, description, and suggestion

Diff:
{code_diff}

Return in this JSON format:
{{
  "issues": [
    {{
      "type": "style",
      "line": 10,
      "description": "Line too long",
      "suggestion": "Split into multiple lines"
    }}
  ],
  "summary": {{
    "total_issues": X,
    "critical_issues": Y
  }}
}}
"""
    response = llm.invoke(prompt)
    try:
        import json
        return json.loads(response)
    except Exception:
        return {"error": "Failed to parse model response", "raw": response}
