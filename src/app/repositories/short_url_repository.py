from typing import Sequence

from sqlalchemy import select, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.app.core.exceptions import SlugAlreadyExistsError, SlugNotFoundError
from src.app.models.short_url import ShortUrl


class ShortUrlRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_url(self, original_url: str, slug: str, owner_id: int) -> ShortUrl:
        new_url = ShortUrl(original_url=original_url, slug=slug, owner_id=owner_id)
        self.session.add(new_url)
        try:
            await self.session.flush()
            return new_url
        except IntegrityError:
            raise SlugAlreadyExistsError(f"Url with slug {slug} already exists")

    async def get_url(self, slug: str) -> ShortUrl:
        result = await self.session.execute(
            select(ShortUrl).where(ShortUrl.slug == slug)
        )
        url = result.scalar_one_or_none()
        if not url:
            raise SlugNotFoundError(f"Url with slug {slug} not found")
        return url

    async def increment_clicks(self, slug: str) -> None:
        url = await self.get_url(slug)
        url.clicks += 1
        await self.session.flush()

    async def get_urls_owner(
        self, owner_id: int, reverse: bool = False, page: int = 1, limit: int = 10
    ) -> Sequence[ShortUrl]:
        offset = (page - 1) * limit
        query = (
            select(ShortUrl)
            .where(ShortUrl.owner_id == owner_id)
            .limit(limit)
            .offset(offset)
        )
        if reverse:
            query = query.order_by(asc(ShortUrl.created_at))
        else:
            query = query.order_by(desc(ShortUrl.created_at))
        result = await self.session.execute(query)
        return result.scalars().all()
