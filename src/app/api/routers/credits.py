from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.app.api.deps import get_current_user
from src.app.models.user import User


class CreditsInfo(BaseModel):
    credits: int

    model_config = {"from_attributes": True}


router = APIRouter(tags=["credits"], prefix="/credits")


@router.get("")
async def get_my_credits(
    user: Annotated[User, Depends(get_current_user)],
) -> CreditsInfo:
    return CreditsInfo.model_validate(user)
