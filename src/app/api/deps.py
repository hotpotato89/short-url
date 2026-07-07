from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated, Any, AsyncGenerator

from src.app.core.database import SessionLocal
from src.app.core.exceptions import InvalidTokenError, PermissionDeniedError
from src.app.models.user import User
from src.app.repositories.click import ClickRepository
from src.app.repositories.export_log_repository import ExportLogRepository
from src.app.repositories.refresh_token_reposiotry import RefreshTokenRepository
from src.app.repositories.short_url_repository import ShortUrlRepository
from src.app.repositories.user_repository import UserRepository
from src.app.services.click_service import ClickService
from src.app.services.export_service import ExportService
from src.app.services.qrcode_service import QrcodeService
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


async def get_refresh_token_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RefreshTokenRepository:
    return RefreshTokenRepository(session)


async def get_log_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ExportLogRepository:
    return ExportLogRepository(session)


async def get_click_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ClickRepository:
    return ClickRepository(session)


# Service dependencies


async def get_qrcode_service(
    url_repo: Annotated[ShortUrlRepository, Depends(get_url_repo)],
) -> QrcodeService:
    return QrcodeService(url_repo)


async def get_export_service(
    url_repo: Annotated[ShortUrlRepository, Depends(get_url_repo)],
    log_repo: Annotated[ExportLogRepository, Depends(get_log_repo)],
) -> ExportService:
    return ExportService(url_repo, log_repo)


async def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    refresh_token_repo: Annotated[
        RefreshTokenRepository, Depends(get_refresh_token_repo)
    ],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserService:
    return UserService(user_repo, refresh_token_repo, session)


async def get_click_service(
    click_repo: Annotated[ClickRepository, Depends(get_click_repo)],
    url_repo: Annotated[ShortUrlRepository, Depends(get_url_repo)],
) -> ClickService:
    return ClickService(click_repo, url_repo)


async def get_url_service(
    url_repo: Annotated[ShortUrlRepository, Depends(get_url_repo)],
    session: Annotated[AsyncSession, Depends(get_session)],
    qrcode_service: Annotated[QrcodeService, Depends(get_qrcode_service)],
    export_service: Annotated[ExportService, Depends(get_export_service)],
) -> ShortUrlService:
    return ShortUrlService(url_repo, session, qrcode_service, export_service)


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
) -> User | None:
    return await repo.get_user(user_data["email"])


async def get_current_admin(
    user_data: Annotated[dict[str, Any], Depends(get_token_payload)],
    repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> User | None:
    if user_data["role"] != "admin":
        raise PermissionDeniedError("Only for admins")
    return await repo.get_user(user_data["email"])
