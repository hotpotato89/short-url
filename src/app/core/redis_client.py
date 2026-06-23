from redis.asyncio import Redis

from src.app.core.settings import settings


redis_client = Redis.from_url(settings.redis.cache_url, decode_responses=True)
