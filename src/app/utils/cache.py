import asyncio
from datetime import datetime
from decimal import Decimal
from functools import wraps
import hashlib
import inspect
import json
from typing import Any, Callable, ParamSpec, TypeVar, cast

from src.app.core.logging import get_logger
from src.app.core.redis_client import redis_client

T = TypeVar("T")
P = ParamSpec("P")

logger = get_logger(__name__)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        if hasattr(obj, "hex"):
            return str(obj)
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def _gen_cache_key(
    func_name: str,
    args: tuple,
    kwargs: dict,
    prefix: str | None = None,
) -> str:
    cleaned_args = args[1:] if args and hasattr(args[0], "__class__") else args
    sorted_kwargs = dict(sorted(kwargs.items()))

    data = {
        "func_name": func_name,
        "args": cleaned_args,
        "kwargs": sorted_kwargs,
    }

    key_hash = hashlib.sha256(
        json.dumps(data, default=str, sort_keys=True).encode()
    ).hexdigest()

    base_key = f"cache:{key_hash}"
    if prefix:
        return f"cache:{prefix}:{key_hash}"
    return base_key


def cache(
    ttl: int, prefix: str | None = None
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def wrapper(func: Callable[P, T]) -> Callable[P, T]:
        if not inspect.iscoroutinefunction(func):
            raise TypeError(
                f"@cache can only be used on async functions. "
                f"'{func.__name__}' is sync."
            )

        @wraps(func)
        async def inner(*args: P.args, **kwargs: P.kwargs) -> T:
            cache_key = _gen_cache_key(func.__name__, args, kwargs, prefix)

            try:
                cached = await redis_client.get(cache_key)
                if cached:
                    logger.debug("Cache HIT", cache_key=cache_key)
                    if cached == "__NULL__":
                        return None  # type: ignore
                    return json.loads(cached)
            except Exception as exc:
                logger.warning(
                    "Failed cache get",
                    cache_key=cache_key,
                    error=str(exc),
                    exc_info=True,
                )

            result = await func(*args, **kwargs)

            try:
                if result is None:
                    data_to_cache = "__NULL__"
                else:
                    data_to_cache = json.dumps(result, cls=CustomJSONEncoder)
                await redis_client.set(cache_key, data_to_cache, ex=ttl)
                logger.debug("Cache saved", cache_key=cache_key)
            except Exception as exc:
                logger.warning(
                    "Failed cache set",
                    cache_key=cache_key,
                    error=str(exc),
                    exc_info=True,
                )

            return result

        return cast(Callable[P, T], inner)

    return wrapper


async def invalidate_cache(prefix: str = "*") -> int:
    if prefix == "*":
        pattern = "cache:*"
    else:
        pattern = f"cache:{prefix}:*"

    logger.debug("Starting cache invalidation", pattern=pattern)

    deleted_count = 0
    cursor = 0
    start_time = asyncio.get_event_loop().time()
    timeout = 30

    try:
        while True:
            if asyncio.get_event_loop().time() - start_time > timeout:
                logger.warning("Cache invalidation timed out", timeout_seconds=timeout)
                break

            cursor, keys = await redis_client.scan(
                cursor,
                match=pattern,
                count=100,
            )

            if keys:
                await redis_client.delete(*keys)
                deleted_count += len(keys)

            if cursor == 0:
                break

        logger.info("Cache invalidated", deleted_count=deleted_count)
        return deleted_count

    except Exception as exc:
        logger.error(
            "Failed to invalidate cache",
            error=str(exc),
            exc_info=True,
        )
        return deleted_count
