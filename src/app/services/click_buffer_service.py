from redis.asyncio import Redis


class ClickBuffer:
    def __init__(self, redis_client: Redis) -> None:
        self.redis_client = redis_client

    async def incr_count(self, slug: str, amount: int) -> None:
        await self.redis_client.incr(f"click:{slug}", amount)