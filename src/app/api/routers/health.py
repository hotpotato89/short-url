from fastapi import APIRouter, status
from pydantic import BaseModel


router = APIRouter(tags=["health"], prefix="/health")


class StatusInfo(BaseModel):
    status: str = "ok"


@router.get("")
async def health() -> StatusInfo:
    return StatusInfo()


@router.head("", status_code=status.HTTP_200_OK)
async def health_head() -> None:
    return None
