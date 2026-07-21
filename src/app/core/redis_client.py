from redis.asyncio import Redis
from simple_redis_cache.asyncio import Cache

from src.app.core.settings import settings

redis_client = Redis.from_url(settings.redis.cache_url, decode_responses=False)
cache_manager = Cache(redis_client)  # type: ignore
