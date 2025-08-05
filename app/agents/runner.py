from app.agents.tools import fetch_diff, analyze_code_diff

def run_agent(repo_url: str, pr_number: int):
    print(f"[DEBUG] Running agent on repo: {repo_url}, PR: {pr_number}")
    
    # 1. Call the fetch_diff tool properly
    diff = fetch_diff.invoke({"repo_url": repo_url, "pr_number": pr_number})

    # 2. Analyze it
    result = analyze_code_diff.invoke({"code_diff": diff})

    return result
