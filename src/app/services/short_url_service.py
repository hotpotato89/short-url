import asyncio
from logging import getLogger
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.database import SessionLocal
from src.app.services.qrcode_service import QrcodeService
from src.app.utils.cache import cache, invalidate_cache
from src.app.core.exceptions import PermissionDeniedError, SlugAlreadyExistsError
from src.app.repositories.short_url_repository import ShortUrlRepository
from src.app.schemas.short_url import UrlCreate, UrlEdit, UrlResponse
from src.app.utils.retry import retry
from src.app.utils.slug import generate_slug


logger = getLogger(__name__)
URL_KEY_FIELD: str = "url"


class ShortUrlService:
    def __init__(self, repo: ShortUrlRepository, session: AsyncSession, qr_service: QrcodeService) -> None:
        self.repo = repo
        self.session = session
        self.qr_service = qr_service

    @retry(SlugAlreadyExistsError)
    async def create(self, url_data: UrlCreate, owner_id: int) -> UrlResponse:
        original_url = str(url_data.original_url)
        slug = generate_slug(6)
        result = await self.repo.create_url(original_url, slug, owner_id)
        await self.session.commit()
        return UrlResponse.model_validate(result)

    @cache(prefix=URL_KEY_FIELD)
    async def get_url(self, slug: str) -> str:
        result = await self.repo.get_url(slug)
        asyncio.create_task(self._increment_clicks(slug))
        return result.original_url

    async def get_my_urls(
        self, owner_id: int, reverse: bool = False, page: int = 1, limit: int = 10
    ) -> Sequence[UrlResponse]:
        result = await self.repo.get_urls_owner(owner_id, reverse, page, limit)
        return [UrlResponse.model_validate(url) for url in result]

    async def edit_slug(
        self, exist_slug: str, edit_data: UrlEdit, user_id: int
    ) -> UrlResponse:
        url = await self.repo.get_url(exist_slug)
        if url.owner_id != user_id:
            raise PermissionDeniedError("You don't have permission")

        result = await self.repo.edit_slug(exist_slug, edit_data.slug)
        await invalidate_cache(URL_KEY_FIELD)
        await self.qr_service.invalidate_qrcode_cache(exist_slug)
        await self.qr_service.invalidate_qrcode_cache(edit_data.slug)
        await self.session.commit()
        return UrlResponse.model_validate(result)

    async def delete_url(self, slug: str, user_id: int) -> None:
        url = await self.repo.get_url(slug)
        if url.owner_id != user_id:
            raise PermissionDeniedError("You don't have permission")
        await self.repo.delete_url(slug)
        await invalidate_cache(URL_KEY_FIELD)
        await self.session.commit()

    async def _increment_clicks(self, slug: str) -> None:
        try:
            async with SessionLocal() as session:
                repo = ShortUrlRepository(session)
                await repo.increment_clicks(slug)
                await session.commit()
        except Exception as e:
            logger.error("Unhandled error %s", e)
