from logging import getLogger

from celery import shared_task

from src.app.core.database import CelerySessionLocal
from src.app.repositories.celery import CeleryRepository


logger = getLogger(__name__)


@shared_task
def increment_clicks_task(slug: str) -> None:
    with CelerySessionLocal() as session:
        repo = CeleryRepository(session)
        repo.increment_clicks(slug)


@shared_task
def delete_expired() -> None:
    with CelerySessionLocal() as session:
        repo = CeleryRepository(session)
        deleted = repo.delete_expired()
        logger.info("Deleted %s expired urls", deleted)
