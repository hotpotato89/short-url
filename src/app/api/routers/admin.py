from fastapi import APIRouter, Depends, Path, Query

from typing import Annotated, Sequence

from src.app.api.deps import get_current_admin, get_user_service
from src.app.models.user import User
from src.app.schemas.user import ChangeRole, UserResponse
from src.app.services.user_service import UserService


router = APIRouter(
    tags=["admin"],
    prefix="/admin"
)


@router.patch("/users/{user_id}/role")
async def change_role(
    service: Annotated[UserService, Depends(get_user_service)],
    admin: Annotated[User, Depends(get_current_admin)],
    user_id: Annotated[int, Path(..., ge=1, description="User ID")],
    role_data: ChangeRole,
) -> UserResponse:
    return await service.change_role(user_id, admin.id, role_data.role)


@router.get("/users")
async def get_all(
    service: Annotated[UserService, Depends(get_user_service)],
    admin: Annotated[User, Depends(get_current_admin)],
    limit: int = Query(100, ge=1, le=1000, description="Count of records on 1 page"),
) -> Sequence[UserResponse]:
    return await service.get_all(limit)
