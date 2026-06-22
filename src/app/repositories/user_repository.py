from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

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
