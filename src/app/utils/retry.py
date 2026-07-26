import asyncio
from collections.abc import Callable
from functools import wraps


def retry(exc: type[Exception], retries: int = 5, delay: float = 0.1):
    def wrapper(func: Callable):
        @wraps(func)
        async def inner(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except exc as e:
                    if attempt == retries - 1:
                        raise e
                    await asyncio.sleep(delay * (attempt + 1))

        return inner

    return wrapper
