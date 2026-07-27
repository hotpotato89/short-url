from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

from sqlalchemy import asc, delete, desc, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.exceptions import SlugAlreadyExistsError, SlugNotFoundError
from src.app.models.short_url import ShortUrl
from src.app.models.user import User


class ShortUrlRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_url(
        self, original_url: str, slug: str, owner_id: int, ttl_days: int | None
    ) -> ShortUrl:
        ttl = datetime.now(UTC) + timedelta(days=ttl_days) if ttl_days else None
        new_url = ShortUrl(
            original_url=original_url, slug=slug, owner_id=owner_id, expires_at=ttl
        )
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

    async def get_url_by_id(self, url_id: int) -> ShortUrl:
        result = await self.session.execute(
            select(ShortUrl).where(ShortUrl.id == url_id)
        )
        url = result.scalar_one_or_none()
        if not url:
            raise SlugNotFoundError(f"Url with ID {url_id} not found")
        return url

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

    async def edit_slug(self, exist_slug: str, new_slug: str) -> ShortUrl:
        result = await self.session.execute(
            select(ShortUrl).where(ShortUrl.slug == exist_slug)
        )
        url = result.scalar_one_or_none()
        if not url:
            raise SlugNotFoundError(f"Url with slug {exist_slug} not found")
        url.slug = new_slug
        try:
            await self.session.flush()
            return url
        except IntegrityError:
            raise SlugAlreadyExistsError(f"Slug {new_slug} already taken")

    async def delete_url(self, slug: str) -> None:
        url = await self.get_url(slug)
        await self.session.delete(url)
        await self.session.flush()

    async def get_all(self, limit: int = 10000) -> Sequence[ShortUrl]:
        result = await self.session.execute(
            select(ShortUrl).limit(limit).order_by(ShortUrl.created_at.desc())
        )
        return result.scalars().all()

    async def increment_click(self, url_id: int) -> None:
        stmt = (
            update(ShortUrl)
            .values(clicks=ShortUrl.clicks + 1)
            .where(ShortUrl.id == url_id)
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def delete_expired(self) -> int:
        stmt = delete(ShortUrl).where(ShortUrl.expires_at < datetime.now(UTC))
        result = await self.session.execute(stmt)
        await self.session.flush()
        if hasattr(result, "rowcount"):
            return result.rowcount
        else:
            return 0

    async def replenish_credits(self, amount: int) -> None:
        stmt = (
            update(User).values(credits=User.credits + amount).where(User.credits < 5)
        )
        await self.session.execute(stmt)
        await self.session.flush()
