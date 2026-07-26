from datetime import UTC

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.exceptions import SlugNotFoundError
from src.app.repositories.short_url_repository import ShortUrlRepository


@pytest.fixture()
async def repo(db_session: AsyncSession) -> ShortUrlRepository:
    return ShortUrlRepository(db_session)


async def test_increment_click(repo: ShortUrlRepository) -> None:
    """Проверяем инкремент кликов через url_id"""
    url = await repo.create_url(
        original_url="https://example.com",
        slug="test123",
        owner_id=1,
        ttl_days=None,
    )

    assert url.clicks == 0

    await repo.increment_click(url.id)

    updated = await repo.get_url("test123")
    assert updated.clicks == 1


async def test_increment_click_twice(repo: ShortUrlRepository) -> None:
    """Проверяем двойной инкремент"""
    url = await repo.create_url(
        original_url="https://example.com",
        slug="test456",
        owner_id=1,
        ttl_days=None,
    )

    assert url.clicks == 0

    await repo.increment_click(url.id)
    await repo.increment_click(url.id)

    updated = await repo.get_url("test456")
    assert updated.clicks == 2


async def test_increment_click_not_found(repo: ShortUrlRepository) -> None:
    """Проверяем, что при несуществующем url_id ничего не падает (просто не обновляется)"""
    # Просто вызываем метод с несуществующим id
    # Если метод не выбрасывает исключение — тест проходит
    await repo.increment_click(99999)

    # Проверяем, что метод отработал без ошибок
    # (это всё, что нужно проверить)
    assert True


async def test_delete_expired(repo: ShortUrlRepository) -> None:
    """Проверяем удаление просроченных ссылок"""
    from datetime import datetime, timedelta, timezone

    # Создаём просроченную ссылку
    expired_at = datetime.now(UTC) - timedelta(days=1)
    url = await repo.create_url(
        original_url="https://expired.com",
        slug="expired",
        owner_id=1,
        ttl_days=None,
    )
    url.expires_at = expired_at
    await repo.session.flush()

    # Создаём активную ссылку
    await repo.create_url(
        original_url="https://active.com",
        slug="active",
        owner_id=1,
        ttl_days=30,
    )

    deleted = await repo.delete_expired()
    assert deleted == 1

    with pytest.raises(SlugNotFoundError):
        await repo.get_url("expired")

    # Активная ссылка должна остаться
    active = await repo.get_url("active")
    assert active.original_url == "https://active.com"


async def test_get_urls_owner(repo: ShortUrlRepository) -> None:
    """Проверяем получение ссылок владельца"""
    await repo.create_url(
        original_url="https://example1.com",
        slug="test1",
        owner_id=1,
        ttl_days=None,
    )
    await repo.create_url(
        original_url="https://example2.com",
        slug="test2",
        owner_id=1,
        ttl_days=None,
    )
    await repo.create_url(
        original_url="https://example3.com",
        slug="test3",
        owner_id=2,
        ttl_days=None,
    )

    urls = await repo.get_urls_owner(owner_id=1)
    assert len(urls) == 2
    assert urls[0].slug in ["test1", "test2"]


async def test_get_urls_owner_pagination(repo: ShortUrlRepository) -> None:
    """Проверяем пагинацию в get_urls_owner"""
    for i in range(10):
        await repo.create_url(
            original_url=f"https://example{i}.com",
            slug=f"test{i}",
            owner_id=1,
            ttl_days=None,
        )

    page1 = await repo.get_urls_owner(owner_id=1, page=1, limit=5)
    page2 = await repo.get_urls_owner(owner_id=1, page=2, limit=5)

    assert len(page1) == 5
    assert len(page2) == 5
    assert page1[0].id != page2[0].id


async def test_replenish_credits(
    repo: ShortUrlRepository, db_session: AsyncSession
) -> None:
    """Проверяем пополнение кредитов"""
    from src.app.models.user import User

    # Создаём пользователей
    user1 = User(email="user1@example.com", password_hash="hash1", credits=3)
    user2 = User(email="user2@example.com", password_hash="hash2", credits=7)
    db_session.add(user1)
    db_session.add(user2)
    await db_session.flush()

    await repo.replenish_credits(amount=5)

    await db_session.refresh(user1)
    await db_session.refresh(user2)

    # Проверяем, что credits обновились (где было < 5)
    assert user1.credits == 8  # 3 + 5
    assert user2.credits == 7  # 7 не изменилось (>= 5)
