import base64
from datetime import datetime
from typing import Annotated, Literal, Sequence

from fastapi import (
    APIRouter,
    Depends,
    Path,
    Query,
    Request,
    Response,
    status,
)
from fastapi.responses import RedirectResponse

from src.app.api.deps import (
    get_current_admin,
    get_current_user,
    get_qrcode_service,
    get_url_service,
)
from src.app.core.logging import get_logger
from src.app.models.user import User
from src.app.schemas.short_url import UrlCreate, UrlEdit, UrlResponse
from src.app.services.qrcode_service import QrcodeService
from src.app.services.short_url_service import ShortUrlService
from src.app.core.limiter import limiter
from src.app.core.task_runner import task_runner
from src.app.tasks import increment_clicks_task

BASE_LIMIT: str = "5/min"
router = APIRouter(tags=["url"], prefix="/url")
logger = get_logger(__name__)


@router.post("")
@limiter.limit(BASE_LIMIT)
async def shorten(
    request: Request,
    url_data: UrlCreate,
    service: Annotated[ShortUrlService, Depends(get_url_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UrlResponse | None:
    return await service.create(url_data, current_user.id, url_data.ttl_days)


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
    request: Request,
    service: Annotated[ShortUrlService, Depends(get_url_service)],
    slug: str = Path(..., max_length=20),
) -> RedirectResponse:

    url = await service.get_url(slug)
    logger.debug("Sending task for slug", slug=slug)
    task_runner.run_in_bg(increment_clicks_task, slug)
    logger.debug("Task sent for slug", slug=slug)
    return RedirectResponse(url, status_code=status.HTTP_303_SEE_OTHER)


@router.get("/{slug}/info")
async def get_url_info(
    service: Annotated[ShortUrlService, Depends(get_url_service)],
    user: Annotated[User, Depends(get_current_user)],
    slug: str = Path(..., max_length=20, description="Url's slug"),
) -> UrlResponse:
    return await service.get_info(user.id, user.role, slug)


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
    export_service: Annotated[ShortUrlService, Depends(get_url_service)],
    format: Literal["csv", "json", "xlsx"] = Query("csv"),
) -> Response:
    content = await export_service.export_all_urls(format)

    if format == "xlsx":
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        extension = "xlsx"
    elif format == "csv":
        media_type = "text/csv"
        extension = "csv"
    else:
        media_type = "application/json"
        extension = "json"

    filename = f"urls_{datetime.now().strftime('%Y_%m_%d_%H_%M')}.{extension}"

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
