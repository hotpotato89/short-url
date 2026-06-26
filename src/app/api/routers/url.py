import base64
from datetime import datetime, timezone
from logging import getLogger
from typing import Annotated, Literal, Sequence

from fastapi import APIRouter, Depends, Path, Query, Request, Response, status
from fastapi.responses import RedirectResponse

from src.app.api.deps import (
    get_current_admin,
    get_current_user,
    get_qrcode_service,
    get_url_service,
)
from src.app.models.user import User
from src.app.schemas.short_url import UrlCreate, UrlEdit, UrlResponse
from src.app.services.qrcode_service import QrcodeService
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


@router.get("/{slug}/qr")
async def get_qrcode(
    service: Annotated[QrcodeService, Depends(get_qrcode_service)],
    slug: str = Path(..., max_length=20, description="Slug of url"),
) -> Response:
    qr_base64 = await service.get_qrcode(slug)
    qr_bytes = base64.b64decode(qr_base64)

    return Response(
        content=qr_bytes,
        media_type="image/png",
    )


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


@router.get("/admin/export")
async def export_all(
    _: Annotated[User, Depends(get_current_admin)],
    service: Annotated[ShortUrlService, Depends(get_url_service)],
    format: Literal["csv", "json"] = Query("csv", description="Output data format"),
) -> Response:
    """
    Export all data, only for admins
    Formats: csv and json
    """

    content = await service.export_all_urls(format)

    media_type = "text/csv" if format == "csv" else "application/json"
    filename = f"urls_{datetime.now(timezone.utc)}.{format}"

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
