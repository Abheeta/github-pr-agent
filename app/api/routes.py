from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models.schema import AnalyzePRRequest, AnalyzePRResponse, StatusResponse, ResultsResponse
from app.tasks.analyze import analyze_pr_task
from celery.result import AsyncResult
from app.core.celery_app import celery_app
import os

router = APIRouter()

@router.post("/analyze-pr", response_model=AnalyzePRResponse)
def analyze_pr(payload: AnalyzePRRequest):
    task = analyze_pr_task.delay(payload.repo_url, payload.pr_number, payload.github_token)
    return {"task_id": task.id}


@router.get("/status/{task_id}", response_model=StatusResponse)
def get_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    
    return {
        "task_id": task_id,
        "status": result.status,
    }

@router.get("/results/{task_id}", response_model=ResultsResponse)
def get_results(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    full_result = result.result if result.successful() else None
    raw = None

    if full_result and isinstance(full_result, dict):
        raw = full_result.get("results", {}).get("raw")
    print(result, "FULLLRESULTTTTT")
    print({
        "task_id": task_id,
        "status": result.status,
        "results": raw,
        "error": str(result.result) if result.failed() else None,
    })

    return {
        "task_id": task_id,
        "status": result.status,
        "results": raw,
        "error": str(result.result) if result.failed() else None,
    }

