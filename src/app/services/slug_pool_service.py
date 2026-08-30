from typing import Final

from redis.asyncio import Redis

from src.app.core.logging import get_logger
from src.app.core.task_runner import task_runner
from src.app.repositories.short_url_repository import ShortUrlRepository
from src.app.utils.slug import generate_slug

logger = get_logger(__name__)


class SlugPoolService:
    POOL_KEY: Final[str] = "slug_pool"
    BATCH_SIZE: Final[int] = 500
    WATERMARK: Final[int] = 200

    LOCK_KEY: Final[str] = "slug_pool_lock"

    def __init__(self, redis_client: Redis, url_repo: ShortUrlRepository) -> None:
        self.redis_client = redis_client
        self.url_repo = url_repo

    async def gen_unique_slugs(self, batch_size: int = BATCH_SIZE) -> list[str]:
        slugs = []

        for _ in range(batch_size):
            slug = generate_slug()
            if not self.url_repo.check_exists(slug):
                slugs.append(slug)

        return slugs

    async def get_slug(self) -> str:
        slug = await self.redis_client.lpop(self.POOL_KEY)
        if slug:
            is_locked = await self.redis_client.exists(self.LOCK_KEY)
            if (
                not is_locked
                and await self.redis_client.llen(self.POOL_KEY) < self.WATERMARK
            ):
                from src.app.tasks import refill_slug_pool_task

                await task_runner.run_in_bg(refill_slug_pool_task)
            return slug.decode()
        return generate_slug()

    async def refill_slug_pool(self) -> None:
        lock = self.redis_client.lock(self.LOCK_KEY, timeout=10)
        if not await lock.acquire(blocking=False):
            logger.debug("SlugPool lock is already acquired by another instance")
            return

        try:
            logger.info("Started slug pool refilling")
            await self.redis_client.expire(self.LOCK_KEY, 10)

            new_slugs = await self.gen_unique_slugs()
            await self.redis_client.rpush(self.POOL_KEY, *new_slugs)
            logger.info("Finished slug pool refilling", count=len(new_slugs))
        finally:
            await lock.release()
