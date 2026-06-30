import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.exceptions import SlugNotFoundError
from src.app.repositories.short_url_repository import ShortUrlRepository


@pytest.fixture()
async def repo(db_session: AsyncSession) -> ShortUrlRepository:
    return ShortUrlRepository(db_session)


async def test_increment_clicks(repo: ShortUrlRepository) -> None:
    url = await repo.create_url(
        original_url="https://example.com",
        slug="test123",
        owner_id=1,
        ttl_days=None,
    )

    assert url.clicks == 0

    await repo.increment_clicks("test123")

    updated = await repo.get_url("test123")
    assert updated.clicks == 1


async def test_increment_clicks_twice(repo: ShortUrlRepository) -> None:
    url = await repo.create_url(
        original_url="https://example.com",
        slug="test456",
        owner_id=1,
        ttl_days=None,
    )

    assert url.clicks == 0

    await repo.increment_clicks("test456")
    await repo.increment_clicks("test456")

    updated = await repo.get_url("test456")
    assert updated.clicks == 2


async def test_increment_clicks_not_found(repo: ShortUrlRepository) -> None:
    with pytest.raises(SlugNotFoundError):
        await repo.increment_clicks("nonexistent")
