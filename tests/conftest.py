import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from async_argon2 import AsyncArgon2
from faker import Faker
from fakeredis.aioredis import FakeRedis
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr
from simple_redis_cache.asyncio import Cache
from slowapi import Limiter
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.app.api.deps import get_redis_client, get_session
from src.app.core.limiter import limiter
from src.app.main import app
from src.app.models.base import Base
from src.app.models.user import User
from src.app.schemas.click import ClickResponse
from src.app.schemas.pagination import CursorPaginationResponse
from src.app.schemas.token import TokenInfo
from src.app.schemas.user import UserRegister

faker = Faker()
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
test_hasher = AsyncArgon2()


@pytest.fixture
def mock_click_stats():
    with patch("src.app.services.click_service.ClickService.get_stats") as mock:
        mock.return_value = CursorPaginationResponse(
            items=[
                ClickResponse(
                    id=1,
                    url_id=1,
                    user_ip="127.0.0.1",
                    user_agent="TestBot/1.0",
                    created_at=datetime.now(UTC),
                )
            ],
            next_cursor=None,
            limit=10,
            has_more=False,
        )
        yield mock


async def get_test_redis() -> FakeRedis:
    return FakeRedis()


@pytest.fixture(autouse=True)
async def disable_limiter() -> AsyncGenerator[Limiter]:
    limiter.enabled = False
    yield limiter
    limiter.enabled = True


@pytest.fixture(scope="session")
async def db_engine() -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(TEST_DB_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture()
async def db_session(db_engine) -> AsyncGenerator[AsyncSession]:
    TestSesstionLocal = async_sessionmaker(
        db_engine, expire_on_commit=False, class_=AsyncSession
    )

    async with TestSesstionLocal() as session:
        yield session


@pytest.fixture()
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    async def override_db_session():
        yield db_session

    app.dependency_overrides[get_session] = override_db_session
    app.dependency_overrides[get_redis_client] = get_test_redis

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    await db_session.rollback()


@pytest.fixture()
async def fake_user() -> UserRegister:
    return UserRegister(
        email=faker.unique.email(), password=SecretStr(faker.password())
    )


@pytest.fixture()
async def fake_user2() -> UserRegister:
    """Создаёт ещё одного уникального пользователя."""
    return UserRegister(
        email=faker.unique.email(), password=SecretStr(faker.password())
    )


@pytest.fixture()
async def auth_tokens(client: AsyncClient, fake_user: UserRegister) -> TokenInfo:
    reg_resp = await client.post(
        "/auth/register",
        json={
            "email": fake_user.email,
            "password": fake_user.password.get_secret_value(),
        },
    )
    if reg_resp.status_code == 409:
        login_resp = await client.post(
            "/auth/login",
            json={
                "email": fake_user.email,
                "password": fake_user.password.get_secret_value(),
            },
        )
        return TokenInfo(**login_resp.json())

    assert reg_resp.status_code == 200

    login_resp = await client.post(
        "/auth/login",
        json={
            "email": fake_user.email,
            "password": fake_user.password.get_secret_value(),
        },
    )
    assert login_resp.status_code == 200
    return TokenInfo(**login_resp.json())


@pytest.fixture()
async def auth_tokens2(client: AsyncClient, fake_user2: UserRegister) -> TokenInfo:
    reg_resp = await client.post(
        "/auth/register",
        json={
            "email": fake_user2.email,
            "password": fake_user2.password.get_secret_value(),
        },
    )
    if reg_resp.status_code == 409:
        login_resp = await client.post(
            "/auth/login",
            json={
                "email": fake_user2.email,
                "password": fake_user2.password.get_secret_value(),
            },
        )
        return TokenInfo(**login_resp.json())

    assert reg_resp.status_code == 200

    login_resp = await client.post(
        "/auth/login",
        json={
            "email": fake_user2.email,
            "password": fake_user2.password.get_secret_value(),
        },
    )
    assert login_resp.status_code == 200
    return TokenInfo(**login_resp.json())


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    admin = User(
        email=f"admin_{uuid.uuid4()}@example.com",
        password_hash=await test_hasher.hash("admin123"),
        role="admin",
        is_superadmin=False,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest.fixture
async def admin_tokens(client: AsyncClient, admin_user: User) -> TokenInfo:
    login_resp = await client.post(
        "/auth/login",
        json={
            "email": admin_user.email,
            "password": "admin123",
        },
    )
    assert login_resp.status_code == 200
    return TokenInfo(**login_resp.json())


@pytest.fixture
async def superadmin_user(db_session: AsyncSession) -> User:
    admin = User(
        email=f"superadmin_{uuid.uuid4()}@example.com",
        password_hash=await test_hasher.hash("superadmin123"),
        role="admin",
        is_superadmin=True,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest.fixture
async def superadmin_tokens(
    client: AsyncClient,
    superadmin_user: User,
) -> TokenInfo:
    login_resp = await client.post(
        "/auth/login",
        json={
            "email": superadmin_user.email,
            "password": "superadmin123",
        },
    )
    assert login_resp.status_code == 200
    return TokenInfo(**login_resp.json())
