from typing import AsyncGenerator

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

from src.app.api.deps import get_session
from src.app.main import app
from src.app.models.base import Base
from src.app.schemas.token import TokenInfo
from src.app.schemas.user import UserRegister
from src.app.utils.jwt import create_access_token


faker = Faker()
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


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
async def auth_token(client: AsyncClient, fake_user: UserRegister) -> str:
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

    return login_data.access_token


@pytest.fixture()
async def auth_token2(client: AsyncClient, fake_user2: UserRegister) -> str:
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

    return login_data.access_token
