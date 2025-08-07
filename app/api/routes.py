from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models.schema import AnalyzePRRequest, AnalyzePRResponse, StatusResponse, ResultsResponse
from app.tasks.analyze import analyze_pr_task
from celery.result import AsyncResult
from app.core.celery_app import celery_app, TaskResultManager
import os

router = APIRouter()

@router.post("/analyze-pr", response_model=AnalyzePRResponse)
def analyze_pr(payload: AnalyzePRRequest):
    webhook_url = str(payload.webhook_url) if payload.webhook_url else None
    task = analyze_pr_task.delay(payload.repo_url, payload.pr_number, payload.github_token, webhook_url)
    
    # Set initial pending status in Redis
    TaskResultManager.set_task_status(task.id, "pending")
    
    return {"task_id": task.id}


@router.get("/status/{task_id}", response_model=StatusResponse)
def get_status(task_id: str):
    # Try to get status from Redis first
    redis_result = TaskResultManager.get_task_result(task_id)
    
    if redis_result:
        return {
            "task_id": task_id,
            "status": redis_result["status"],
        }
    
    # If result not found, raise 404
    raise HTTPException(status_code=404, detail=f"Task ID {task_id} not found")


@router.get("/results/{task_id}", response_model=ResultsResponse)
def get_results(task_id: str):
    # Get results from Redis
    redis_result = TaskResultManager.get_task_result(task_id)
    
    if redis_result:
        return {
            "task_id": task_id,
            "status": redis_result["status"],
            "results": redis_result["results"],
            "error": redis_result["error"],
        }
    
    # If result not found, raise 404
    raise HTTPException(status_code=404, detail=f"Task ID {task_id} not found")