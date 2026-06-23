from typing import Annotated

from fastapi import APIRouter, Body, Depends, Request, status

from src.app.api.deps import get_current_user, get_user_service
from src.app.models.user import User
from src.app.schemas.token import TokenInfo
from src.app.schemas.user import UserLogin, UserRegister, UserResponse
from src.app.services.user_service import UserService
from src.app.core.limiter import limiter


router = APIRouter(tags=["auth"], prefix="/auth")
BASE_LIMIT: str = "5/min"


@router.post("/register")
@limiter.limit(BASE_LIMIT)
async def register(
    request: Request,
    service: Annotated[UserService, Depends(get_user_service)],
    register_data: UserRegister,
) -> UserResponse:
    return await service.register(register_data)


@router.post("/login")
@limiter.limit(BASE_LIMIT)
async def login(
    request: Request,
    service: Annotated[UserService, Depends(get_user_service)],
    login_data: UserLogin,
) -> TokenInfo:
    return await service.login(login_data)


@router.get("/me")
async def me(current_user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.post("/refresh")
@limiter.limit(BASE_LIMIT)
async def refresh(
    request: Request,
    service: Annotated[UserService, Depends(get_user_service)],
    refresh_token: str = Body(..., embed=True),
) -> TokenInfo:
    return await service.refresh(refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    service: Annotated[UserService, Depends(get_user_service)],
    refresh_token: str = Body(..., embed=True),
) -> None:
    return await service.logout(refresh_token)
