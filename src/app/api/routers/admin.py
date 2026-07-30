from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response

from src.app.api.deps import (
    get_current_admin,
    get_export_service,
    get_url_service,
    get_user_service,
)
from src.app.core.enums import ExportFormat
from src.app.core.task_runner import task_runner
from src.app.models.user import User
from src.app.schemas.export_log import ExportLogResponse
from src.app.schemas.pagination import CursorPaginationResponse
from src.app.schemas.user import ChangeRole, UserResponse
from src.app.services.export_service import ExportService
from src.app.services.short_url_service import ShortUrlService
from src.app.services.user_service import UserService
from src.app.tasks import save_export_log_task

router = APIRouter(tags=["admin"], prefix="/admin")


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
    limit: int = Query(10, ge=1, le=100, description="Count of records on 1 page"),
    cursor: int | None = Query(None, description="Pagination cursor (ID)"),
) -> CursorPaginationResponse[UserResponse]:
    return await service.get_all(admin.role, limit, cursor)


@router.get("/export")
async def export_all(
    admin: Annotated[User, Depends(get_current_admin)],
    export_service: Annotated[ShortUrlService, Depends(get_url_service)],
    format: ExportFormat = ExportFormat.CSV,
) -> Response:
    content = await export_service.export_all_urls(format)
    await task_runner.run_in_bg(save_export_log_task, admin.id, format)

    if format == "xlsx":
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        extension = "xlsx"
    elif format == "csv":
        media_type = "text/csv"
        extension = "csv"
    else:
        media_type = "application/json"
        extension = "json"

    filename = f"urls_{datetime.now(UTC).strftime('%Y_%m_%d_%H_%M')}.{extension}"

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export-logs")
async def get_logs(
    admin: Annotated[User, Depends(get_current_admin)],
    service: Annotated[ExportService, Depends(get_export_service)],
    limit: int = Query(100, ge=1, le=500, description="limit of records count"),
    cursor: int | None = Query(None, description="Pagination cursor (ID)"),
) -> CursorPaginationResponse[ExportLogResponse]:
    return await service.get_logs(admin.is_superadmin, limit=limit, cursor=cursor)
