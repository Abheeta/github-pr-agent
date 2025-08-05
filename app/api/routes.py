from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models.schema import AnalyzePRRequest, AnalyzePRResponse, StatusResponse
from app.tasks.analyze import analyze_pr_task
from celery.result import AsyncResult
import os

router = APIRouter()


@router.post("/analyze-pr", response_model=AnalyzePRResponse)
def analyze_pr(payload: AnalyzePRRequest):
    task = analyze_pr_task.delay(payload.repo_url, payload.pr_number)
    return {"task_id": task.id}


@router.get("/status/{task_id}", response_model=StatusResponse)
def get_status(task_id: str):
    result = AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.successful() else None,
        "error": str(result.result) if result.failed() else None,
    }
