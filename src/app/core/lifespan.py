from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from src.app.core.database import engine
from src.app.core.logging import get_logger, setup_logging
from src.app.core.redis_client import redis_client
from src.app.core.taskiq_broker import broker

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()

    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    logger.info("Database connected")

    await redis_client.ping()
    logger.info("Redis connected")

    if not broker.is_worker_process:
        await broker.startup()

    yield

    if not broker.is_worker_process:
        await broker.shutdown()

    await redis_client.close()
    logger.info("Redis disconnected")

    await engine.dispose()
    logger.info("Database disconnected")
