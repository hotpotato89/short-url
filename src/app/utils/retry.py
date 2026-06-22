from functools import wraps
from typing import Callable, Type
import asyncio


def retry(exc: Type[Exception], retries: int = 5, delay: float = 0.1):
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
