import asyncio

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.repositories.click import ClickRepository


class ClickBuffer:
    def __init__(
        self, redis_client: Redis, db_session: AsyncSession, repo: ClickRepository
    ) -> None:
        self.redis_client = redis_client
        self.session = db_session
        self.repo = repo

    async def incr_count(self, slug: str, amount: int) -> None:
        await self.redis_client.incr(f"click:{slug}", amount)

    async def __flush_all(self, batch_size: int = 100, timeout_seconds: int = 30) -> dict[str, int]:
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
