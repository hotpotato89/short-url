from logging import getLogger
from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Path, Query, Request, status
from fastapi.responses import RedirectResponse

from src.app.api.deps import get_current_user, get_url_service
from src.app.models.user import User
from src.app.schemas.short_url import UrlCreate, UrlEdit, UrlResponse
from src.app.services.short_url_service import ShortUrlService
from src.app.core.limiter import limiter


logger = getLogger(__name__)
BASE_LIMIT: str = "5/min"
router = APIRouter(tags=["url"], prefix="/url")


@router.post("")
@limiter.limit(BASE_LIMIT)
async def shorten(
    request: Request,
    url_data: UrlCreate,
    service: Annotated[ShortUrlService, Depends(get_url_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UrlResponse | None:
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
    logger.info("Redirected from %s to %s", slug, url)
    return RedirectResponse(url, status_code=status.HTTP_308_PERMANENT_REDIRECT)


@router.put("/{slug}")
@limiter.limit(BASE_LIMIT)
async def edit_slug(
    request: Request,
    service: Annotated[ShortUrlService, Depends(get_url_service)],
    edit_data: UrlEdit,
    current_user: Annotated[User, Depends(get_current_user)],
    slug: str = Path(..., max_length=20, description="Slug of url"),
) -> UrlResponse:
    return await service.edit_slug(slug, edit_data, current_user.id)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(BASE_LIMIT)
async def delete_url(
    request: Request,
    service: Annotated[ShortUrlService, Depends(get_url_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    slug: str = Path(..., max_length=20, description="Slug of url"),
) -> None:
    await service.delete_url(slug, current_user.id)
