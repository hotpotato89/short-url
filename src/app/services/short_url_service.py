from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.exceptions import PermissionDeniedError
from src.app.repositories.short_url_repository import ShortUrlRepository
from src.app.schemas.short_url import UrlCreate, UrlEdit, UrlResponse
from src.app.utils.slug import generate_slug


class ShortUrlService:
    def __init__(self, repo: ShortUrlRepository, session: AsyncSession) -> None:
        self.repo = repo
        self.session = session

    async def create(self, url_data: UrlCreate, owner_id: int) -> UrlResponse:
        original_url = str(url_data.original_url)
        slug = generate_slug(6)
        result = await self.repo.create_url(original_url, slug, owner_id)
        await self.session.commit()
        return UrlResponse.model_validate(result)

    async def get_url(self, slug: str) -> str:
        result = await self.repo.get_url(slug)
        await self.repo.increment_clicks(slug)
        await self.session.commit()
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
        await self.session.commit()
        return UrlResponse.model_validate(result)

    async def delete_url(self, slug: str, user_id: int) -> None:
        url = await self.repo.get_url(slug)
        if url.owner_id != user_id:
            raise PermissionDeniedError("You don't have permission")
        await self.repo.delete_url(slug)
        await self.session.commit()
