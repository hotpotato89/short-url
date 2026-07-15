from logging import getLogger

from async_argon2 import AsyncArgon2

from src.app.core.settings import settings

logger = getLogger(__name__)

hasher = AsyncArgon2(
    logger=logger,
    time_cost=settings.argon2.time_cost,
    memory_cost=settings.argon2.memory_cost,
    parallelism=settings.argon2.parallelism,
    hash_len=settings.argon2.hash_len,
    salt_len=settings.argon2.salt_len,
)
