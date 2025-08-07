import requests
from app.agents.graph import graph
from celery import current_task
from app.core.celery_app import TaskResultManager
from celery.result import AsyncResult
from app.core.celery_app import celery_app

def run_agent(repo_url: str, pr_number: int, github_token: str = None, webhook_url: str = None):
    task_id = current_task.request.id
    print(f"[DEBUG] Running agent on repo: {repo_url}, PR: {pr_number}")

    # Set initial status as processing
    TaskResultManager.set_task_status(task_id, "processing")

    initial_state = {
        "repo_url": repo_url,
        "pr_number": pr_number,
        "github_token": github_token
    }

    try:
        final_state = graph.invoke(initial_state)
        result_data = final_state.get("result", {})
        print(final_state, "FINAL STATE")

        # Store successful results in Redis
        TaskResultManager.set_task_status(task_id, "completed", results=result_data)

        payload = {
            "task_id": task_id,
            "status": "completed",
            "results": result_data,
            "error": None
        }

    except Exception as e:
        # Store failure in Redis
        error_message = str(e)
        TaskResultManager.set_task_status(task_id, "failed", error=error_message)
        
        result_data = {}
        payload = {
            "task_id": task_id,
            "status": "failed",
            "results": None,
            "error": error_message
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