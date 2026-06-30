from celery import Celery
from celery.schedules import crontab

from src.app.core.settings import settings

from src.app.models.user import User  # noqa
import src.app.models  # noqa


celery_app = Celery(
    "short_url", broker=settings.redis.celery_url, backend=settings.redis.celery_url
)

celery_app.autodiscover_tasks(["src.app.tasks"])

celery_app.conf.update(
    beat_schedule={
        "delete_expired_urls": {
            "task": "src.app.tasks.delete_expired",
            "schedule": crontab(hour=3, minute=0),
        },
    },
    timezone="UTC",
    enable_utc=True,
)
