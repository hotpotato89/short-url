from functools import wraps
import hashlib
import json
from typing import Callable

from app.core.redis_client import redis_client


def cache(ttl: int = 3600, prefix: str | None = None):
    def wrapper(func: Callable):
        @wraps(func)
        async def inner(*args, **kwargs):
            cache_key = _gen_cache_key(func.__name__, args, kwargs, prefix)

            cached = await redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            result = await func(*args, **kwargs)

            await redis_client.setex(cache_key, ttl, json.dumps(result, default=str))
            return result

        return inner

    return wrapper


def _gen_cache_key(
    func_name: str, args: tuple, kwargs: dict, prefix: str | None = None
) -> str:
    sorted_kwargs = dict(sorted(kwargs.items()))

    data = {
        "func_name": func_name,
        "args": args,
        "kwargs": sorted_kwargs,
    }

    key_hash = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

    if prefix:
        return f"cache:{prefix}:{key_hash}"
    return f"cache:{key_hash}"


async def invalidate_cache(prefix: str = "*") -> None:
    keys = await redis_client.keys(f"cache:{prefix}")
    if keys:
        await redis_client.delete(*keys)
