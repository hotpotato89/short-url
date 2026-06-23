from contextlib import asynccontextmanager
from logging import getLogger

from sqlalchemy import text
from fastapi import FastAPI

from src.app.core.database import engine
from src.app.core.redis_client import redis_client


logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):

    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    logger.info("Database connected")

    await redis_client.ping()
    logger.info("Redis connected")

    yield

    await redis_client.close()
    logger.info("Redis disconnected")

    await engine.dispose()
    logger.info("Database disconnected")
