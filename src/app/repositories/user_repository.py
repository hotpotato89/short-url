from typing import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.app.core.enums import UserRole
from src.app.core.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_user(self, email: str, password_hash: str) -> User:
        new_user = User(email=email, password_hash=password_hash)

        self.session.add(new_user)
        try:
            await self.session.flush()
            return new_user
        except IntegrityError:
            raise UserAlreadyExistsError(f"User with login {email} already exists")

    async def get_user(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def change_role(self, user_id: int, new_role: UserRole) -> User | None:
        user = await self.session.get(User, user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        user.role = new_role
        await self.session.flush()
        return user

    async def get_all(self, limit: int = 100) -> Sequence[User]:
        result = await self.session.execute(
            select(User).limit(limit).order_by(User.id.desc())
        )
        return result.scalars().all()

    async def decrement_credits(self, user_id: int) -> bool:
        stmt = update(User).where(User.id == user_id, User.credits >= 1).values(credits=User.credits - 1)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0  # type: ignore
