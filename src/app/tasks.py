from src.app.core.redis_client import redis_client
from src.app.core.database import SessionLocal
from src.app.core.enums import ExportFormat
from src.app.core.logging import get_logger
from src.app.core.taskiq_broker import broker
from src.app.repositories.click import ClickRepository
from src.app.repositories.export_log_repository import ExportLogRepository
from src.app.repositories.short_url_repository import ShortUrlRepository
from src.app.services.slug_pool_service import SlugPoolService

logger = get_logger(__name__)


@broker.task
async def increment_click_task(url_id: int) -> None:
    async with SessionLocal() as session:
        repo = ShortUrlRepository(session)
        await repo.increment_click(url_id)
        await session.commit()


@broker.task
async def save_click_task(url_id: int, user_ip: str, user_agent: str) -> None:
    async with SessionLocal() as session:
        repo = ClickRepository(session)
        await repo.save_click(url_id, user_ip, user_agent)
        await session.commit()


@broker.task
async def save_export_log_task(user_id: int, format: ExportFormat) -> None:
    async with SessionLocal() as session:
        repo = ExportLogRepository(session)
        await repo.save_export_logs(user_id, format)
        await session.commit()


@broker.task
async def refill_slug_pool_task() -> None:
    service = SlugPoolService(redis_client)
    await service.refill_slug_pool()


@broker.task(schedule=[{"cron": "0 0 1 * *"}])
async def replenish_credits_task() -> None:
    async with SessionLocal() as session:
        repo = ShortUrlRepository(session)
        await repo.replenish_credits(5)
        await session.commit()


@broker.task(schedule=[{"cron": "0 0 * * *"}])
async def delete_expired_task() -> None:
    async with SessionLocal() as session:
        repo = ShortUrlRepository(session)
        deleted = await repo.delete_expired()
        logger.info("Deleted expired urls", count=deleted)
        await session.commit()
