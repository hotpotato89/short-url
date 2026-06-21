import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient, ASGITransport

from src.app.api.deps import get_session
from src.app.main import app
from src.app.models.base import Base


TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture()
async def db_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture()
async def db_session(db_engine):
    TestSesstionLocal = async_sessionmaker(
        db_engine, expire_on_commit=False, class_=AsyncSession
    )

    async with TestSesstionLocal() as session:
        yield session


@pytest.fixture()
async def client(db_session):
    async def override_db_session():
        yield db_session

    app.dependency_overrides[get_session] = override_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
