from redis.asyncio import Redis
from simple_redis_cache.asyncio import Cache

from src.app.core.logging import get_logger
from src.app.core.settings import settings


logger = get_logger(__name__)
redis_client = Redis.from_url(settings.redis.cache_url, decode_responses=True)
cache_manager = Cache(redis_client, logger)  # type: ignore
