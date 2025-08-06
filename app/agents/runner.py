from app.agents.tools import fetch_diff, analyze_code_diff
from app.agents.graph import graph

def run_agent(repo_url: str, pr_number: int, github_token: str = None):
    print(f"[DEBUG] Running agent on repo: {repo_url}, PR: {pr_number}")

    # Initial input state
    initial_state = {
        "repo_url": repo_url,
        "pr_number": pr_number,
        "github_token": github_token
    }

    # Invoke the graph with the initial state
    final_state: AgentState = graph.invoke(initial_state)

    print("[DEBUG] Final state:", final_state)
    return final_state["result"]  # or return entire final_state if needed
