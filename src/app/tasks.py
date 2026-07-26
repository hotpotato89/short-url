from src.app.core.taskiq_broker import push_broker


from src.app.repositories.short_url_repository import ShortUrlRepository
from src.app.core.database import SessionLocal


@push_broker.task
async def increment_click_task(url_id: int) -> None:
    async with SessionLocal() as session:
        repo = ShortUrlRepository(session)
        await repo.increment_click(url_id)
