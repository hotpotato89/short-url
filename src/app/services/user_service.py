from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.enums import UserRole
from src.app.core.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    PermissionDeniedError,
    UserNotFoundError,
)
from src.app.repositories.refresh_token_reposiotry import RefreshTokenRepository
from src.app.repositories.user_repository import UserRepository
from src.app.schemas.token import TokenInfo
from src.app.schemas.user import UserLogin, UserRegister, UserResponse
from src.app.core.hashing import hasher
from src.app.utils.jwt import create_access_token, create_refresh_token, decode_jwt
from src.app.utils.crypt import crypt_util


class UserService:
    def __init__(
        self,
        repo: UserRepository,
        refresh_token_repo: RefreshTokenRepository,
        session: AsyncSession,
    ) -> None:
        self.repo = repo
        self.refresh_token_repo = refresh_token_repo
        self.session = session

    async def register(self, register_data: UserRegister) -> UserResponse:
        result = await self.repo.create_user(
            register_data.email,
            await hasher.hash(register_data.password.get_secret_value()),
        )
        await self.session.commit()
        return UserResponse.model_validate(result)

    async def login(self, login_data: UserLogin) -> TokenInfo:
        user = await self.repo.get_user(login_data.email)
        if not user or not await hasher.verify(
            login_data.password.get_secret_value(), user.password_hash
        ):
            raise InvalidCredentialsError("Invalid email or password")

        access_token = create_access_token(user.id, user.email, user.role)
        refresh_token = create_refresh_token(user.id, user.email, user.role)

        hashed = crypt_util.hash(refresh_token)
        await self.refresh_token_repo.create(user.id, hashed)
        await self.session.commit()

        return TokenInfo(access_token=access_token, refresh_token=refresh_token)

    async def refresh(self, refresh_token: str) -> TokenInfo:
        token_payload = decode_jwt(refresh_token)
        if token_payload.get("type") != "refresh":
            raise InvalidTokenError("Invalid token type")

        hashed = crypt_util.hash(refresh_token)
        existing_token = await self.refresh_token_repo.get_by_token(hashed)
        if not existing_token:
            raise InvalidTokenError("Token not found")

        user_id = int(token_payload["sub"])
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")

        new_refresh_token = create_refresh_token(user.id, user.email, user.role)
        access_token = create_access_token(user.id, user.email, user.role)

        await self.refresh_token_repo.delete_by_token(hashed)
        await self.refresh_token_repo.create(
            user.id, crypt_util.hash(new_refresh_token)
        )
        await self.session.commit()

        return TokenInfo(access_token=access_token, refresh_token=new_refresh_token)

    async def logout(self, refresh_token: str) -> None:
        encrypted = crypt_util.hash(refresh_token)
        await self.refresh_token_repo.delete_by_token(encrypted)
        await self.session.commit()

    async def change_role(
        self, user_id: int, admin_id: int, role: UserRole = UserRole.USER
    ) -> UserResponse:
        user = await self.repo.get_by_id(user_id)

        if user:
            if user.is_superadmin:
                raise PermissionDeniedError("You can not edit super admin's role")
            if user.id == admin_id:
                raise PermissionDeniedError("You can not edit your role")

        result = await self.repo.change_role(user_id, role)
        await self.session.commit()
        return UserResponse.model_validate(result)

    async def get_all(self, limit: int = 100) -> Sequence[UserResponse]:
        users = await self.repo.get_all(limit)
        return [UserResponse.model_validate(user) for user in users]
