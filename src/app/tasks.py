from celery import shared_task

from src.app.core.database import CelerySessionLocal
from src.app.repositories.celery import CeleryRepository


@shared_task
def increment_clicks_task(slug: str) -> None:
    with CelerySessionLocal() as session:
        repo = CeleryRepository(session)
        repo.increment_clicks(slug)


@shared_task
def delete_expired() -> None:
    with CelerySessionLocal() as session:
        repo = CeleryRepository(session)
        repo.delete_expired()
