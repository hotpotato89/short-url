from typing import Final

from redis.asyncio import Redis

from src.app.utils.slug import generate_slug


class SlugPoolService:

    POOL_KEY: Final[str] = "slug_pool"
    BATCH_SIZE: Final[int] = 500
    WATERMARK: Final[int] = 200

    LOCK_KEY: Final[str] = "slug_pool_lock"

    def __init__(self, redis_client: Redis) -> None:
        self.redis_client = redis_client

    async def get_slug(self) -> str:
        slug = await self.redis_client.lpop(self.POOL_KEY)
        if slug:
            if await self.redis_client.llen(self.POOL_KEY) < self.WATERMARK:
                ...
            return slug.decode()
        return generate_slug()

    async def refill_slug_pool(self) -> None:
        if not await self.redis_client.setnx(self.LOCK_KEY, 1):
            return

        try:
            await self.redis_client.expire(self.LOCK_KEY, 10)

            new_slugs = [generate_slug() for _ in range(self.BATCH_SIZE)]
            await self.redis_client.rpush(self.POOL_KEY, *new_slugs)
        finally:
            await self.redis_client.delete(self.LOCK_KEY)

    