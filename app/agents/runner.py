import requests
from app.agents.graph import graph
from celery import current_task

def run_agent(repo_url: str, pr_number: int, github_token: str = None, webhook_url: str = None):
    task_id = current_task.request.id
    print(f"[DEBUG] Running agent on repo: {repo_url}, PR: {pr_number}")

    initial_state = {
        "repo_url": repo_url,
        "pr_number": pr_number,
        "github_token": github_token
    }

    try:
        final_state = graph.invoke(initial_state)
        result_data = final_state.get("result", {})
        raw = final_state.get("result", {}).get("raw")
        print(final_state, "FINAL STATE")

        payload = {
            "task_id": task_id,
            "status": "SUCCESS",
            "results": raw,
            "error": None
        }

    except Exception as e:
        # If the graph or anything else fails
        result_data = {}
        payload = {
            "task_id": task_id,
            "status": "FAILURE",
            "results": None,
            "error": str(e)
        }

    # Fire webhook, non-blocking, logs errors if any
    if webhook_url:
        try:
            print(f"[DEBUG] Calling webhook: {webhook_url}")
            requests.post(webhook_url, json=payload, timeout=10)
        except Exception as webhook_error:
            print(f"[ERROR] Webhook call failed: {webhook_error}")

    # Final return value (unchanged)
    return result_data
