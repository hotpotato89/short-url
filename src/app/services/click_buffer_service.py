import asyncio
from typing import Final

from redis.asyncio import Redis

from src.app.core.logging import get_logger
from src.app.repositories.short_url_repository import ShortUrlRepository

logger = get_logger(__name__)


class ClickBuffer:
    LOCK_KEY: Final[str] = "click_buffer_lock"
    TIMEOUT_SECONDS: Final[int] = 30
    BATCH_SIZE: Final[int] = 100

    def __init__(self, redis_client: Redis, repo: ShortUrlRepository) -> None:
        self.redis_client = redis_client
        self.repo = repo

    async def incr_count(self, slug: str, amount: int) -> None:
        await self.redis_client.incr(f"click:{slug}", amount)

    async def __flush_all(
        self, batch_size: int = 100, timeout_seconds: int = 30
    ) -> dict[str, int]:
        cursor = 0
        all_clicks = {}
        started_at = asyncio.get_event_loop().time()

        while True:
            if asyncio.get_event_loop().time() - started_at > timeout_seconds:
                break

            cursor, keys = await self.redis_client.scan(cursor, "clicks:*", batch_size)

            if not keys:
                if cursor == 0:
                    break
                continue

            async with self.redis_client.pipeline() as pipe:
                for key in keys:
                    pipe.get(key)
                    pipe.delete(key)
                values = await pipe.execute()

            for i, key in enumerate(keys):
                slug = key.decode().replace("clicks:", "")
                count = int(values[i * 2])
                all_clicks[slug] = count
        return all_clicks

    async def push(
        self, batch_size: int = BATCH_SIZE, timeout_seconds: int = TIMEOUT_SECONDS
    ) -> bool | None:
        lock = self.redis_client.lock(self.LOCK_KEY, timeout=timeout_seconds)
        acquired = await lock.acquire(blocking=False)
        if not acquired:
            return

        try:
            clicks = await self.__flush_all(batch_size, timeout_seconds)

            if not clicks:
                logger.debug("Clicks is empty")
                return True

            await self.repo.bulk_increment_clicks(clicks)
            return True
        except Exception as exc:
            logger.exception("Unhandled error", error=str(exc))
            return False
        finally:
            await lock.release()
