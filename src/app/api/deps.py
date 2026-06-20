from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated, Any, AsyncGenerator

from src.app.core.database import SessionLocal
from src.app.core.exceptions import InvalidTokenError
from src.app.models.user import User
from src.app.repositories.short_url_repository import ShortUrlRepository
from src.app.repositories.user_repository import UserRepository
from src.app.services.short_url_service import ShortUrlService
from src.app.services.user_service import UserService
from src.app.utils.jwt import decode_jwt


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


# Repository dependencies


async def get_user_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepository:
    return UserRepository(session)


async def get_url_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ShortUrlRepository:
    return ShortUrlRepository(session)


# Service dependencies


async def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserService:
    return UserService(user_repo, session)


async def get_url_service(
    url_repo: Annotated[ShortUrlRepository, Depends(get_url_repo)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ShortUrlService:
    return ShortUrlService(url_repo, session)


# Jwt dependencies

security = HTTPBearer(auto_error=True)


async def get_token_payload(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> dict[str, Any]:
    payload = decode_jwt(token.credentials)
    if payload["type"] != "access":
        raise InvalidTokenError("Invalid token type")
    return payload


async def get_current_user(
    user_data: Annotated[dict[str, Any], Depends(get_token_payload)],
    repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> User:
    return await repo.get_user(user_data["email"])
