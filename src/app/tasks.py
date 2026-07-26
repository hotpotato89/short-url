from src.app.core.enums import ExportFormat
from src.app.core.taskiq_broker import broker


from src.app.repositories.short_url_repository import ShortUrlRepository
from src.app.repositories.click import ClickRepository
from src.app.repositories.export_log_repository import ExportLogRepository


from src.app.core.database import SessionLocal


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
