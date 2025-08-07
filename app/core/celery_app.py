from celery import Celery
import redis
import os
import json
from typing import Dict, Any, Optional

# 🛠 Ensure redis_url is a string, even if pulled from env or a URL parser
redis_url = str(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

celery_app = Celery(
    "code_review",
    broker=redis_url,
    backend=redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
)

# Redis client for custom result storage
redis_client = redis.from_url(redis_url, decode_responses=True)

class TaskResultManager:
    """Manage task results in Redis with custom status tracking"""
    
    @staticmethod
    def get_task_key(task_id: str) -> str:
        return f"task_result:{task_id}"
    
    @staticmethod
    def set_task_status(task_id: str, status: str, results: Optional[Dict[Any, Any]] = None, error: Optional[str] = None):
        """Set task status and results in Redis"""
        key = TaskResultManager.get_task_key(task_id)
        data = {
            "task_id": task_id,
            "status": status,
            "results": results,
            "error": error
        }
        # Store for 24 hours (86400 seconds)
        redis_client.setex(key, 86400, json.dumps(data))
    
    @staticmethod
    def get_task_result(task_id: str) -> Optional[Dict[str, Any]]:
        """Get task result from Redis"""
        key = TaskResultManager.get_task_key(task_id)
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    
    @staticmethod
    def delete_task_result(task_id: str):
        """Delete task result from Redis"""
        key = TaskResultManager.get_task_key(task_id)
        redis_client.delete(key)