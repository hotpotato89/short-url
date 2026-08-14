# tests/test_click_buffer.py
import asyncio
import pytest
from unittest.mock import AsyncMock, patch
from fakeredis.aioredis import FakeRedis
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.services.click_buffer_service import ClickBuffer
from src.app.repositories.short_url_repository import ShortUrlRepository


@pytest.fixture
async def fake_redis():
    """Создаёт FakeRedis для тестов"""
    redis = FakeRedis()
    yield redis
    await redis.flushall()


@pytest.fixture
async def click_buffer(db_session: AsyncSession, fake_redis):
    """ClickBuffer с FakeRedis"""
    repo = ShortUrlRepository(db_session)
    return ClickBuffer(fake_redis, repo)


@pytest.mark.asyncio
async def test_incr_count(click_buffer, fake_redis):
    """Тест: incr_count увеличивает счётчик в Redis"""
    await click_buffer.incr_count("test_slug", 5)
    
    value = await fake_redis.get("clicks:test_slug")
    assert int(value) == 5


@pytest.mark.asyncio
async def test_flush_all_empty(click_buffer, fake_redis):
    """Тест: __flush_all когда нет ключей"""
    await fake_redis.delete("clicks:*")
    
    result = await click_buffer._ClickBuffer__flush_all()
    
    assert result == {}


@pytest.mark.asyncio
async def test_flush_all_with_keys(click_buffer, fake_redis):
    """Тест: __flush_all с ключами"""
    await fake_redis.set("clicks:slug1", 10)
    await fake_redis.set("clicks:slug2", 5)
    
    result = await click_buffer._ClickBuffer__flush_all()
    
    assert result == {"slug1": 10, "slug2": 5}
    assert await fake_redis.get("clicks:slug1") is None
    assert await fake_redis.get("clicks:slug2") is None


@pytest.mark.asyncio
async def test_push_no_clicks(click_buffer, fake_redis):
    """Тест: push когда нет кликов"""
    await fake_redis.delete("clicks:*")
    
    # Мокаем lock (FakeRedis не поддерживает Lua)
    with patch("redis.asyncio.lock.Lock.acquire", AsyncMock(return_value=True)):
        with patch("redis.asyncio.lock.Lock.release", AsyncMock()):
            with patch.object(click_buffer, "_ClickBuffer__flush_all", AsyncMock(return_value={})):
                await click_buffer.push()


@pytest.mark.asyncio
async def test_push_lock_busy(click_buffer, fake_redis):
    """Тест: push когда блокировка занята"""
    with patch("redis.asyncio.lock.Lock.acquire", AsyncMock(return_value=False)):
        with patch.object(click_buffer, "_ClickBuffer__flush_all", AsyncMock()) as mock_flush:
            await click_buffer.push()
            mock_flush.assert_not_called()


@pytest.mark.asyncio
async def test_push_exception(click_buffer, fake_redis):
    """Тест: push при ошибке — ловит исключение"""
    with patch("redis.asyncio.lock.Lock.acquire", AsyncMock(return_value=True)):
        with patch("redis.asyncio.lock.Lock.release", AsyncMock()):
            with patch.object(
                click_buffer,
                "_ClickBuffer__flush_all",
                AsyncMock(side_effect=Exception("Redis error"))
            ):
                await click_buffer.push()  # не должно упасть


@pytest.mark.asyncio
async def test_push_cancelled(click_buffer, fake_redis):
    """Тест: push при отмене задачи — перебрасывает CancelledError"""
    with patch("redis.asyncio.lock.Lock.acquire", AsyncMock(return_value=True)):
        with patch("redis.asyncio.lock.Lock.release", AsyncMock()):
            with patch.object(
                click_buffer,
                "_ClickBuffer__flush_all",
                AsyncMock(side_effect=asyncio.CancelledError())
            ):
                with pytest.raises(asyncio.CancelledError):
                    await click_buffer.push()