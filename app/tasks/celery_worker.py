from core.celery_app import celery_app
import tasks.analyze

if __name__ == "__main__":
    celery_app.start()
