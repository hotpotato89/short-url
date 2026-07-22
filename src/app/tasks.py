from typing import Literal
from celery import shared_task

from src.app.core.database import CelerySessionLocal
from src.app.core.enums import ExportFormat
from src.app.core.logging import get_logger
from src.app.repositories.celery import CeleryRepository

logger = get_logger(__name__)


@shared_task
def increment_clicks_task(slug: str) -> None:
    with CelerySessionLocal() as session:
        repo = CeleryRepository(session)
        repo.increment_clicks(slug)
        logger.info("Incremented clicks", slug=slug)


@shared_task
def save_click_task(url_id: int, user_ip: str, user_agent: str) -> None:
    with CelerySessionLocal() as session:
        repo = CeleryRepository(session)
        repo.save_click(url_id, user_ip, user_agent)
        logger.info("Saved click", url_id=url_id)


@shared_task
def delete_expired_task() -> None:
    with CelerySessionLocal() as session:
        repo = CeleryRepository(session)
        deleted = repo.delete_expired()
        logger.info("Deleted expired urls", count=deleted)


@shared_task
def save_export_log_task(user_id: int, format: ExportFormat) -> None:
    with CelerySessionLocal() as session:
        repo = CeleryRepository(session)
        repo.save_export_logs(user_id, format)
        logger.info("Saved export log", user_id=user_id, format=format)

@shared_task
def replenish_credits_task() -> None:
    with CelerySessionLocal() as session:
        repo = CeleryRepository(session)
        repo.replenish_credits(5)
