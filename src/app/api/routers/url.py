from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import RedirectResponse

from src.app.api.deps import get_current_user, get_url_service
from src.app.models.user import User
from src.app.schemas.short_url import UrlCreate, UrlResponse
from src.app.services.short_url_service import ShortUrlService


router = APIRouter(tags=["url"], prefix="/url")


@router.post("")
async def shorten(
    url_data: UrlCreate,
    service: Annotated[ShortUrlService, Depends(get_url_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UrlResponse:
    return await service.create(url_data, current_user.id)


@router.get("/my")
async def get_my(
    service: Annotated[ShortUrlService, Depends(get_url_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    reverse: bool = Query(False, description="If oldest first = False, else True"),
    page: int = Query(1, ge=1, description="Page of records"),
    limit: int = Query(10, ge=1, le=50, description="Count of records in page"),
) -> Sequence[UrlResponse]:
    return await service.get_my_urls(current_user.id, reverse, page, limit)


@router.get("/{slug}")
async def redirect(
    service: Annotated[ShortUrlService, Depends(get_url_service)],
    slug: str = Path(..., max_length=20, description="Slug of url"),
) -> RedirectResponse:
    url = await service.get_url(slug)
    return RedirectResponse(url)
