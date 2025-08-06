from app.core.celery_app import celery_app
from app.agents.runner import run_agent


@celery_app.task(name="app.tasks.analyze.analyze_pr_task")
def analyze_pr_task(repo_url: str, pr_number: int, github_token: str = None):
    print(f"Received task with repo_url={repo_url}, pr_number={pr_number}")
    try:
        result = run_agent(repo_url, pr_number, github_token)
        return {
            "status": "completed",
            "results": result
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }
