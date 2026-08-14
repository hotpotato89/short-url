from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.app.core.settings import settings

engine = create_async_engine(
    settings.db.url,
    pool_size=10,
    max_overflow=15,
    pool_pre_ping=True,
    pool_recycle=60 * 60,
)

SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession]:
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
