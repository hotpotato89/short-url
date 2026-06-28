from functools import wraps
import hashlib
import json
from logging import getLogger
from typing import Callable

from src.app.core.redis_client import redis_client

logger = getLogger(__name__)


def cache(ttl: int = 3600, prefix: str | None = None):
    def wrapper(func: Callable):
        @wraps(func)
        async def inner(*args, **kwargs):
            cache_key = _gen_cache_key(func.__name__, args, kwargs, prefix)

            cached = await redis_client.get(cache_key)
            if cached:
                logger.debug("Cache hit: %s", cache_key)
                return json.loads(cached)

            result = await func(*args, **kwargs)

            await redis_client.setex(cache_key, ttl, json.dumps(result, default=str))
            logger.debug("Cache missed and saved: %s", cache_key)
            return result

        return inner

    return wrapper


def _gen_cache_key(
    func_name: str, args: tuple, kwargs: dict, prefix: str | None = None
) -> str:
    clean_args = args[1:] if args and hasattr(args[0], "__class__") else args
    sorted_kwargs = dict(sorted(kwargs.items()))

    data = {
        "func_name": func_name,
        "args": clean_args,
        "kwargs": sorted_kwargs,
    }

    key_hash = hashlib.sha256(
        json.dumps(data, sort_keys=True, default=str).encode()
    ).hexdigest()

    if prefix:
        return f"cache:{prefix}:{key_hash}"
    return f"cache:{key_hash}"


async def invalidate_cache(prefix: str = "*") -> None:
    if prefix == "*":
        keys = await redis_client.keys(f"cache:{prefix}")
    else:
        keys = await redis_client.keys(f"cache:{prefix}:*")
    logger.debug('Found keys: %s', *keys)
    if keys:
        await redis_client.delete(*keys)
        logger.debug("Cache invalidated: %s", *keys)
