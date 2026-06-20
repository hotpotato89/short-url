from typing import Annotated

from fastapi import APIRouter, Depends

from src.app.api.deps import get_user_service
from src.app.schemas.user import UserRegister, UserResponse
from src.app.services.user_service import UserService


router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/register")
async def register(
    service: Annotated[UserService, Depends(get_user_service)],
    register_data: UserRegister,
) -> UserResponse:
    return await service.register(register_data)
