from celery import Celery

from src.app.core.settings import settings


celery_app = Celery(
    "short_url", broker=settings.redis.celery_url, backend=settings.redis.celery_url
)

celery_app.autodiscover_tasks(["src.app.tasks"])
