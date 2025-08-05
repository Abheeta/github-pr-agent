from celery import Celery
import os

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
