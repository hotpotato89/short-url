from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated, AsyncGenerator

from src.app.core.database import SessionLocal
from src.app.repositories.user_repository import UserRepository
from src.app.services.user_service import UserService


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def get_user_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepository:
    return UserRepository(session)


async def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserService:
    return UserService(user_repo, session)
