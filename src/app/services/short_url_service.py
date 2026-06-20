from sqlalchemy.ext.asyncio import AsyncSession

from src.app.repositories.short_url_repository import ShortUrlRepository
from src.app.schemas.short_url import UrlCreate, UrlResponse
from src.app.utils.slug import generate_slug


class ShortUrlService:
    def __init__(self, repo: ShortUrlRepository, session: AsyncSession) -> None:
        self.repo = repo
        self.session = session

    async def create(self, url_data: UrlCreate, owner_id: int) -> UrlResponse:
        async with self.session.begin():
            original_url = str(url_data.original_url)
            slug = generate_slug(6)
            result = await self.repo.create_url(original_url, slug, owner_id)
            return UrlResponse.model_validate(result)

    async def get_url(self, slug: str) -> str:
        async with self.session.begin():
            result = await self.repo.get_url(slug)
            await self.repo.increment_clicks(slug)
            return result.original_url
