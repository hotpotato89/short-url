from typing import AsyncGenerator
from unittest.mock import patch, AsyncMock

from faker import Faker
from pydantic import SecretStr
import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from httpx import AsyncClient, ASGITransport
from redis.asyncio import Redis
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.app.api.deps import get_session
from src.app.core.limiter import limiter
from src.app.main import app
from src.app.models.base import Base
from src.app.schemas.token import TokenInfo
from src.app.schemas.user import UserRegister
from src.app.utils.jwt import create_access_token


faker = Faker()
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(autouse=True)
async def mock_redis() -> AsyncGenerator[Redis, None]:
    with patch("src.app.utils.cache.redis_client") as mock:
        mock.get = AsyncMock(return_value=None)
        mock.setex = AsyncMock()
        mock.delete = AsyncMock()
        mock.keys = AsyncMock()
        mock.close = AsyncMock(return_values=[])

        yield mock


@pytest.fixture(autouse=True)
async def test_limiter() -> AsyncGenerator[Limiter, None]:
    test_limiter = Limiter(
        key_func=get_remote_address,
        storage_uri=None,
        default_limits=['10/minute']
    )

    with patch('src.app.core.limiter.limiter', test_limiter):
        yield test_limiter


@pytest.fixture(autouse=True)
async def disable_limiter() -> AsyncGenerator[Limiter, None]:
    limiter.enabled = False
    yield limiter
    limiter.enabled = True


@pytest.fixture()
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(TEST_DB_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture()
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    TestSesstionLocal = async_sessionmaker(
        db_engine, expire_on_commit=False, class_=AsyncSession
    )

    async with TestSesstionLocal() as session:
        yield session


@pytest.fixture()
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_db_session():
        yield db_session

    app.dependency_overrides[get_session] = override_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    await db_session.rollback()


@pytest.fixture()
async def fake_user() -> UserRegister:
    return UserRegister(email=faker.email(), password=SecretStr(faker.password()))


@pytest.fixture()
async def fake_user2() -> UserRegister:
    return UserRegister(email=faker.email(), password=SecretStr(faker.password()))


@pytest.fixture()
async def auth_tokens(client: AsyncClient, fake_user: UserRegister) -> TokenInfo:
    await client.post(
        "/auth/register",
        json={
            "email": fake_user.email,
            "password": fake_user.password.get_secret_value(),
        },
    )
    login_resp = await client.post(
        "/auth/login",
        json={
            "email": fake_user.email,
            "password": fake_user.password.get_secret_value(),
        },
    )
    login_data = TokenInfo(**login_resp.json())

    return login_data


@pytest.fixture()
async def auth_tokens2(client: AsyncClient, fake_user2: UserRegister) -> TokenInfo:
    await client.post(
        "/auth/register",
        json={
            "email": fake_user2.email,
            "password": fake_user2.password.get_secret_value(),
        },
    )
    login_resp = await client.post(
        "/auth/login",
        json={
            "email": fake_user2.email,
            "password": fake_user2.password.get_secret_value(),
        },
    )
    login_data = TokenInfo(**login_resp.json())

    return login_data
