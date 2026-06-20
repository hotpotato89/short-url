from src.app.core.exceptions import InvalidCredentialsError
from src.app.repositories.user_repository import UserRepository
from src.app.schemas.token import TokenInfo
from src.app.schemas.user import UserLogin, UserRegister, UserResponse
from src.app.utils.hash import hash_password, verify_password
from src.app.utils.jwt import create_access_token


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    async def register(self, register_data: UserRegister) -> UserResponse:
        result = await self.repo.create_user(
            register_data.email,
            hash_password(register_data.password.get_secret_value()),
        )
        return UserResponse.model_validate(result)

    async def login(self, login_data: UserLogin) -> TokenInfo:
        user = await self.repo.get_user(login_data.email)
        if not user or not verify_password(
            login_data.password.get_secret_value(), user.password_hash
        ):
            raise InvalidCredentialsError("Invalid email or password")

        access_token = create_access_token(user.id, user.email)
        return TokenInfo(access_token=access_token)
