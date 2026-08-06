from unittest.mock import AsyncMock, patch

import pytest
from fakeredis.aioredis import FakeRedis

from src.app.services.slug_pool_service import SlugPoolService


@pytest.fixture
async def redis_client():
    """Создаёт свежий FakeRedis для каждого теста."""
    async with FakeRedis() as redis:
        yield redis


@pytest.fixture
async def slug_pool_service(redis_client):
    """Создаёт SlugPoolService с FakeRedis."""
    return SlugPoolService(redis_client)


async def test_get_slug_returns_from_pool(slug_pool_service):
    """Проверяет, что get_slug возвращает слэг из пула."""
    # 1. Заполняем пул
    await slug_pool_service.refill_slug_pool()

    # 2. Берём слэг
    slug = await slug_pool_service.get_slug()

    # 3. Проверяем
    assert slug is not None
    assert len(slug) == 6  # Длина по умолчанию


async def test_get_slug_fallback_when_pool_empty(slug_pool_service):
    """Проверяет, что при пустом пуле генерируется слэг через generate_slug."""
    # 1. Очищаем пул (удаляем все ключи)
    await slug_pool_service.redis_client.flushdb()

    # 2. Подменяем generate_slug на известное значение
    with patch(
        "src.app.services.slug_pool_service.generate_slug", return_value="abc1234"
    ):
        slug = await slug_pool_service.get_slug()

    # 3. Проверяем
    assert slug == "abc1234"


async def test_refill_slug_pool_fills_redis(slug_pool_service):
    """Проверяет, что refill_slug_pool заполняет Redis."""
    # 1. Очищаем пул
    await slug_pool_service.redis_client.flushdb()

    # 2. Пополняем
    await slug_pool_service.refill_slug_pool()

    # 3. Проверяем, что в Redis появились слэги
    count = await slug_pool_service.redis_client.llen(slug_pool_service.POOL_KEY)
    assert count == slug_pool_service.BATCH_SIZE


async def test_refill_slug_pool_with_lock(slug_pool_service):
    """Проверяет, что блокировка не даёт пополнять пул дважды."""
    # 1. Устанавливаем блокировку
    await slug_pool_service.redis_client.setnx(slug_pool_service.LOCK_KEY, 1)

    # 2. Пытаемся пополнить
    await slug_pool_service.refill_slug_pool()

    # 3. Проверяем, что пул НЕ пополнился (блокировка помешала)
    count = await slug_pool_service.redis_client.llen(slug_pool_service.POOL_KEY)
    assert count == 0


async def test_watermark_triggers_refill(slug_pool_service):
    """Проверяет, что при падении ниже WATERMARK запускается пополнение."""
    # 1. Заполняем пул
    await slug_pool_service.refill_slug_pool()

    # 2. Забираем слэги до уровня ниже WATERMARK
    for _ in range(slug_pool_service.BATCH_SIZE - slug_pool_service.WATERMARK + 1):
        await slug_pool_service.get_slug()

    # 3. Подменяем task_runner.run_in_bg, чтобы проверить вызов
    with patch(
        "src.app.core.task_runner.task_runner.run_in_bg", AsyncMock()
    ) as mock_run:
        # 4. Берём ещё один слэг (должен запустить пополнение)
        await slug_pool_service.get_slug()

        # 5. Проверяем, что пополнение было вызвано
        mock_run.assert_called_once()


async def test_refill_slug_pool_generates_unique_slugs(slug_pool_service):
    """Проверяет, что сгенерированные слэги уникальны."""
    # 1. Пополняем пул
    await slug_pool_service.refill_slug_pool()

    # 2. Забираем все слэги
    slugs = []
    for _ in range(slug_pool_service.BATCH_SIZE):
        slug = await slug_pool_service.get_slug()
        slugs.append(slug)

    # 3. Проверяем, что все слэги уникальны
    assert len(slugs) == len(set(slugs))
