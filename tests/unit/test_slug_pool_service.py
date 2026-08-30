from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fakeredis.aioredis import FakeRedis
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.repositories.short_url_repository import ShortUrlRepository
from src.app.services.slug_pool_service import SlugPoolService


@pytest.fixture
async def redis_client():
    """Создаёт свежий FakeRedis для каждого теста."""
    async with FakeRedis() as redis:
        yield redis


@pytest.fixture
async def url_repo(
    db_session: AsyncSession,
) -> AsyncGenerator[ShortUrlRepository, None]:
    yield ShortUrlRepository(db_session)


@pytest.fixture
async def slug_pool_service(redis_client, url_repo):
    """Создаёт SlugPoolService с FakeRedis."""
    return SlugPoolService(redis_client, url_repo)


# ============================================================================
# Тесты для get_slug
# ============================================================================


async def test_get_slug_returns_from_pool(slug_pool_service):
    """Проверяет, что get_slug возвращает слэг из пула."""
    # Мокаем lock, чтобы избежать evalsha
    with patch.object(slug_pool_service.redis_client, "lock") as mock_lock:
        mock_lock.return_value = AsyncMock()
        mock_lock.return_value.acquire = AsyncMock(return_value=True)
        mock_lock.return_value.release = AsyncMock()

        # Заполняем пул
        await slug_pool_service.refill_slug_pool()

    # Берём слэг
    slug = await slug_pool_service.get_slug()

    # Проверяем
    assert slug is not None
    assert len(slug) == 6  # Длина по умолчанию


async def test_get_slug_fallback_when_pool_empty(slug_pool_service):
    """Проверяет, что при пустом пуле генерируется слэг через generate_slug."""
    # 1. Очищаем пул
    await slug_pool_service.redis_client.flushdb()

    # 2. Подменяем generate_slug на известное значение
    with patch(
        "src.app.services.slug_pool_service.generate_slug", return_value="abc123"
    ):
        slug = await slug_pool_service.get_slug()

    # 3. Проверяем
    assert slug == "abc123"


async def test_get_slug_returns_from_pool_when_watermark_reached(slug_pool_service):
    """Проверяет, что get_slug возвращает слэг и триггерит пополнение при достижении WATERMARK."""
    # Мокаем lock
    with patch.object(slug_pool_service.redis_client, "lock") as mock_lock:
        mock_lock.return_value = AsyncMock()
        mock_lock.return_value.acquire = AsyncMock(return_value=True)
        mock_lock.return_value.release = AsyncMock()

        # Заполняем пул
        await slug_pool_service.refill_slug_pool()

    # Подменяем task_runner.run_in_bg
    with patch(
        "src.app.core.task_runner.task_runner.run_in_bg", AsyncMock()
    ) as mock_run:
        # Забираем слэги до уровня ниже WATERMARK
        for _ in range(slug_pool_service.BATCH_SIZE - slug_pool_service.WATERMARK + 1):
            await slug_pool_service.get_slug()

        # Сбрасываем счётчик вызовов перед последним вызовом
        mock_run.reset_mock()

        # Берём ещё один слэг (должен запустить пополнение)
        slug = await slug_pool_service.get_slug()

        # Проверяем, что слэг вернулся
        assert slug is not None
        assert len(slug) == 6

        # Проверяем, что пополнение было вызвано (хотя бы один раз)
        assert mock_run.call_count >= 1


# ============================================================================
# Тесты для refill_slug_pool
# ============================================================================


async def test_refill_slug_pool_fills_redis(slug_pool_service):
    """Проверяет, что refill_slug_pool заполняет Redis."""
    # Очищаем пул
    await slug_pool_service.redis_client.flushdb()

    # Мокаем lock
    with patch.object(slug_pool_service.redis_client, "lock") as mock_lock:
        mock_lock.return_value = AsyncMock()
        mock_lock.return_value.acquire = AsyncMock(return_value=True)
        mock_lock.return_value.release = AsyncMock()

        # Пополняем
        await slug_pool_service.refill_slug_pool()

    # Проверяем, что в Redis появились слэги
    count = await slug_pool_service.redis_client.llen(slug_pool_service.POOL_KEY)
    assert count == slug_pool_service.BATCH_SIZE


async def test_refill_slug_pool_does_not_fill_if_lock_acquired(slug_pool_service):
    """Проверяет, что если блокировка занята, пополнение не происходит."""
    # Очищаем пул
    await slug_pool_service.redis_client.flushdb()

    # Мокаем lock — возвращаем False при acquire
    with patch.object(slug_pool_service.redis_client, "lock") as mock_lock:
        mock_lock.return_value = AsyncMock()
        mock_lock.return_value.acquire = AsyncMock(return_value=False)

        # Пытаемся пополнить
        await slug_pool_service.refill_slug_pool()

    # Проверяем, что пул НЕ пополнился
    count = await slug_pool_service.redis_client.llen(slug_pool_service.POOL_KEY)
    assert count == 0


async def test_refill_slug_pool_generates_unique_slugs(slug_pool_service):
    """Проверяет, что сгенерированные слэги уникальны."""
    # Мокаем lock
    with patch.object(slug_pool_service.redis_client, "lock") as mock_lock:
        mock_lock.return_value = AsyncMock()
        mock_lock.return_value.acquire = AsyncMock(return_value=True)
        mock_lock.return_value.release = AsyncMock()

        # Пополняем пул
        await slug_pool_service.refill_slug_pool()

    # Забираем все слэги
    slugs = []
    for _ in range(slug_pool_service.BATCH_SIZE):
        slug = await slug_pool_service.get_slug()
        slugs.append(slug)

    # Проверяем, что все слэги уникальны
    assert len(slugs) == len(set(slugs))


async def test_refill_slug_pool_skips_existing_slugs(slug_pool_service):
    """Проверяет, что gen_unique_slugs пропускает уже существующие слэги."""
    # 1. Создаём существующий слэг в БД
    existing_slug = "abcdef"
    with patch(
        "src.app.services.slug_pool_service.generate_slug",
        side_effect=[existing_slug, "xyz123", "qwerty"],
    ):
        # 2. Мокаем get_all_slugs, чтобы он вернул существующий слэг
        with patch.object(
            slug_pool_service.url_repo, "get_all_slugs", AsyncMock()
        ) as mock_get_all:
            mock_get_all.return_value = [existing_slug]

            # Мокаем lock
            with patch.object(slug_pool_service.redis_client, "lock") as mock_lock:
                mock_lock.return_value = AsyncMock()
                mock_lock.return_value.acquire = AsyncMock(return_value=True)
                mock_lock.return_value.release = AsyncMock()

                # Генерируем слэги
                slugs = await slug_pool_service.gen_unique_slugs(batch_size=2)

    # Проверяем, что существующий слэг пропущен, а сгенерированы новые
    assert len(slugs) == 2
    assert "abcdef" not in slugs
    assert "xyz123" in slugs
    assert "qwerty" in slugs


# ============================================================================
# Тесты для gen_unique_slugs
# ============================================================================


async def test_gen_unique_slugs_returns_correct_count(slug_pool_service):
    """Проверяет, что gen_unique_slugs возвращает ровно batch_size слэгов."""
    # Мокаем get_all_slugs — пустой список
    with patch.object(
        slug_pool_service.url_repo, "get_all_slugs", AsyncMock()
    ) as mock_get_all:
        mock_get_all.return_value = []

        # Генерируем слэги
        slugs = await slug_pool_service.gen_unique_slugs(batch_size=10)

    # Проверяем количество
    assert len(slugs) == 10


async def test_gen_unique_slugs_handles_duplicates(slug_pool_service):
    """Проверяет, что gen_unique_slugs не создаёт дубли в одной пачке."""
    # Мокаем get_all_slugs — пустой список
    with patch.object(
        slug_pool_service.url_repo, "get_all_slugs", AsyncMock()
    ) as mock_get_all:
        mock_get_all.return_value = []

        # Мокаем generate_slug, чтобы он возвращал одинаковый слэг несколько раз
        with patch(
            "src.app.services.slug_pool_service.generate_slug",
            side_effect=["aaa111", "aaa111", "bbb222", "ccc333"],
        ):
            slugs = await slug_pool_service.gen_unique_slugs(batch_size=3)

    # Проверяем, что дубли пропущены
    assert len(slugs) == 3
    assert "aaa111" in slugs
    assert "bbb222" in slugs
    assert "ccc333" in slugs


async def test_gen_unique_slugs_stops_after_max_attempts(slug_pool_service):
    """Проверяет, что gen_unique_slugs останавливается после max_attempts."""
    # Мокаем get_all_slugs — пустой список
    with patch.object(
        slug_pool_service.url_repo, "get_all_slugs", AsyncMock()
    ) as mock_get_all:
        mock_get_all.return_value = []

        # Мокаем generate_slug, чтобы он всегда возвращал один и тот же слэг
        with patch(
            "src.app.services.slug_pool_service.generate_slug",
            return_value="aaa111",
        ):
            slugs = await slug_pool_service.gen_unique_slugs(batch_size=10)

