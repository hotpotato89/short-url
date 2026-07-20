from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.enums import ExportFormat, UserRole
from src.app.core.logging import get_logger
from src.app.core.redis_client import cache_manager
from src.app.repositories.user_repository import UserRepository
from src.app.services.export_service import ExportService
from src.app.services.qrcode_service import QrcodeService
from src.app.core.exceptions import (
    PermissionDeniedError,
    SlugAlreadyExistsError,
    SlugNotFoundError,
)
from src.app.repositories.short_url_repository import ShortUrlRepository
from src.app.schemas.short_url import UrlCreate, UrlEdit, UrlResponse
from src.app.utils.retry import retry
from src.app.utils.slug import generate_slug


URL_KEY_FIELD: str = "url"
BASE_CACHE_TTL: int = 3600 * 2
logger = get_logger(__name__)


class ShortUrlService:
    def __init__(
        self,
        repo: ShortUrlRepository,
        user_repo: UserRepository,
        session: AsyncSession,
        qr_service: QrcodeService,
        export_service: ExportService,
    ) -> None:
        self.repo = repo
        self.user_repo = user_repo
        self.session = session
        self.qr_service = qr_service
        self.export_service = export_service

    @retry(SlugAlreadyExistsError)
    async def create(
        self, url_data: UrlCreate, owner_id: int, ttl_days: int | None
    ) -> UrlResponse:
        original_url = str(url_data.original_url)
        slug = generate_slug(6)

        if not await self.user_repo.decrement_credits(owner_id):
            logger.warning("No left credits", user_id=owner_id)
            raise PermissionDeniedError("No credits left")

        result = await self.repo.create_url(original_url, slug, owner_id, ttl_days)
        await self.session.commit()
        return UrlResponse.model_validate(result)

    @cache_manager.cache(ttl=BASE_CACHE_TTL, prefix=URL_KEY_FIELD, use_pickle=True)
    async def get_url(self, slug: str) -> UrlResponse:
        result = await self.repo.get_url(slug)
        if result.is_expired:
            raise SlugNotFoundError(f"URL with slug '{result.slug}' has expired")

        return UrlResponse.model_validate(result)

    async def get_my_urls(
        self, owner_id: int, reverse: bool = False, page: int = 1, limit: int = 10
    ) -> Sequence[UrlResponse]:
        result = await self.repo.get_urls_owner(owner_id, reverse, page, limit)
        return [UrlResponse.model_validate(url) for url in result]

    async def edit_slug(
        self, exist_slug: str, edit_data: UrlEdit, user_id: int
    ) -> UrlResponse:
        url = await self.repo.get_url(exist_slug)
        if not url:
            raise SlugNotFoundError(f"URL with slug '{exist_slug}' not found")

        if url.is_expired:
            raise SlugNotFoundError(f"URL with slug '{exist_slug}' has expired")

        if url.owner_id != user_id:
            raise PermissionDeniedError("You don't have permission")

        result = await self.repo.edit_slug(exist_slug, edit_data.slug)
        await cache_manager.invalidate_cache(URL_KEY_FIELD)
        await self.qr_service.invalidate_qrcode_cache()
        await self.session.commit()
        return UrlResponse.model_validate(result)

    async def delete_url(self, slug: str, user_id: int) -> None:
        url = await self.repo.get_url(slug)
        if not url:
            raise SlugNotFoundError(f"URL with slug '{slug}' not found")

        if url.is_expired:
            raise SlugNotFoundError(f"URL with slug '{slug}' has expired")

        if url.owner_id != user_id:
            raise PermissionDeniedError("You don't have permission")

        await self.repo.delete_url(slug)
        await cache_manager.invalidate_cache(URL_KEY_FIELD)
        await self.qr_service.invalidate_qrcode_cache()
        await self.session.commit()

    async def export_all_urls(self, format: ExportFormat) -> str | bytes:
        return await self.export_service.export(format)

    async def get_info(
        self, user_id: int, user_role: UserRole, slug: str
    ) -> UrlResponse:
        url = await self.repo.get_url(slug)

        if url.owner_id != user_id and user_role != "admin":
            raise PermissionDeniedError("You don't have permission to view it")

        return UrlResponse.model_validate(url)
