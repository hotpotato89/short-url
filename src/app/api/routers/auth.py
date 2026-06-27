from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Request, status

from src.app.api.deps import get_current_admin, get_current_user, get_user_service
from src.app.models.user import User
from src.app.schemas.token import TokenInfo
from src.app.schemas.user import ChangeRole, UserLogin, UserRegister, UserResponse
from src.app.services.user_service import UserService
from src.app.core.limiter import limiter


router = APIRouter(tags=["auth"], prefix="/auth")
BASE_LIMIT: str = "5/min"


@router.post("/register")
@limiter.limit(limit_value=BASE_LIMIT)
async def register(
    request: Request,
    service: Annotated[UserService, Depends(get_user_service)],
    register_data: UserRegister,
) -> UserResponse:
    return await service.register(register_data)


@router.post("/login")
@limiter.limit(limit_value=BASE_LIMIT)
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
@limiter.limit(limit_value=BASE_LIMIT)
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


@router.patch("/admin/users/{user_id}/role")
async def change_role(
    service: Annotated[UserService, Depends(get_user_service)],
    admin: Annotated[User, Depends(get_current_admin)],
    user_id: Annotated[int, Path(..., ge=1, description="User ID")],
    role_data: ChangeRole,
) -> UserResponse:
    return await service.change_role(user_id, admin.id, role_data.role)
