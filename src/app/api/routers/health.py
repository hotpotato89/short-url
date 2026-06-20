from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(tags=["health"], prefix="/health")


class StatusInfo(BaseModel):
    status: str = "ok"


@router.get("")
async def health() -> StatusInfo:
    return StatusInfo()
