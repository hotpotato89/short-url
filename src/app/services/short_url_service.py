import asyncio
import csv
from io import StringIO
import json
from logging import getLogger
from typing import Callable, Literal, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.database import SessionLocal
from src.app.models.short_url import ShortUrl
from src.app.services.qrcode_service import QrcodeService
from src.app.utils.cache import cache, invalidate_cache
from src.app.core.exceptions import (
    PermissionDeniedError,
    SlugAlreadyExistsError,
    SlugNotFoundError,
)
from src.app.repositories.short_url_repository import ShortUrlRepository
from src.app.schemas.short_url import UrlCreate, UrlEdit, UrlResponse
from src.app.utils.retry import retry
from src.app.utils.slug import generate_slug


logger = getLogger(__name__)
URL_KEY_FIELD: str = "url"


class ShortUrlService:
    def __init__(
        self, repo: ShortUrlRepository, session: AsyncSession, qr_service: QrcodeService
    ) -> None:
        self.repo = repo
        self.session = session
        self.qr_service = qr_service

    @retry(SlugAlreadyExistsError)
    async def create(
        self, url_data: UrlCreate, owner_id: int, ttl_days: int | None
    ) -> UrlResponse:
        original_url = str(url_data.original_url)
        slug = generate_slug(6)
        result = await self.repo.create_url(original_url, slug, owner_id, ttl_days)
        await self.session.commit()
        return UrlResponse.model_validate(result)

    @cache(prefix=URL_KEY_FIELD)
    async def get_url(self, slug: str) -> str:
        result = await self.repo.get_url(slug)
        if result.is_expired:
            raise SlugNotFoundError(f"URL with slug '{result.slug}' has expired")
        
        asyncio.create_task(self._increment_clicks(result.slug))

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
        if not url:
            raise SlugNotFoundError(f"URL with slug '{exist_slug}' not found")

        if url.is_expired:
            raise SlugNotFoundError(f"URL with slug '{exist_slug}' has expired")

        if url.owner_id != user_id:
            raise PermissionDeniedError("You don't have permission")

        result = await self.repo.edit_slug(exist_slug, edit_data.slug)
        await invalidate_cache(URL_KEY_FIELD)
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
        await invalidate_cache(URL_KEY_FIELD)
        await self.qr_service.invalidate_qrcode_cache()
        await self.session.commit()

    async def _increment_clicks(self, slug: str) -> None:
        try:
            async with SessionLocal() as session:
                repo = ShortUrlRepository(session)
                await repo.increment_clicks(slug)
                await session.commit()
        except Exception as e:
            logger.error("Unhandled error %s", e)

    async def export_all_urls(self, format: Literal["csv", "json"] = "csv") -> str:
        urls = await self.repo.get_all()

        if format == "csv":
            return self._csv_format(urls)
        elif format == "json":
            return self._json_format(urls)

    def _json_format(self, urls: Sequence) -> str:
        data = []
        for url in urls:
            data.append(
                {
                    "id": url.id,
                    "original_url": url.original_url,
                    "slug": url.slug,
                    "clicks": url.clicks,
                    "owner_id": url.owner_id,
                    "created_at": url.created_at.isoformat(),
                }
            )
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _csv_format(self, urls: Sequence[ShortUrl]) -> str:
        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(
            ["ID", "Original url", "Slug", "Clicks", "Owner ID", "Created at"]
        )

        for url in urls:
            writer.writerow(
                [
                    url.id,
                    url.original_url,
                    url.slug,
                    url.clicks,
                    url.owner_id,
                    url.created_at.isoformat(),
                ]
            )

        return output.getvalue()
