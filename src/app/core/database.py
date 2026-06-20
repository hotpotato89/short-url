from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
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
