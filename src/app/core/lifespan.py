from contextlib import asynccontextmanager
from logging import getLogger

from sqlalchemy import text
from fastapi import FastAPI

from src.app.core.database import engine


logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):

    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    logger.info("Database connected")

    yield

    await engine.dispose()
    logger.info("Database disconnected")
