from core.celery_app import celery_app

# Optional: makes sure tasks are registered
import tasks.analyze

if __name__ == "__main__":
    celery_app.start()
