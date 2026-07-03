import asyncio
import json
from datetime import datetime
from decimal import Decimal
from typing import Optional
from unittest.mock import patch

import pytest

from src.app.utils.cache import cache, invalidate_cache, CustomJSONEncoder


async def test_cache_hit(test_redis):
    async def test_func(x: int, y: int) -> int:
        return x + y

    decorated = cache(ttl=60, prefix="test")(test_func)

    result1 = await decorated(2, 3)
    assert result1 == 5

    result2 = await decorated(2, 3)
    assert result2 == 5

    keys = await test_redis.keys("cache:test:*")
    assert len(keys) == 1


async def test_cache_different_args(test_redis):
    async def test_func(x: int, y: int) -> int:
        return x + y

    decorated = cache(ttl=60, prefix="test")(test_func)

    await decorated(2, 3)
    await decorated(4, 5)

    keys = await test_redis.keys("cache:test:*")
    assert len(keys) == 2


async def test_cache_none_value(test_redis):
    async def test_func(x: int) -> Optional[int]:
        if x == 0:
            return None
        return x * 2

    decorated = cache(ttl=60, prefix="test")(test_func)

    result = await decorated(0)
    assert result is None

    keys = await test_redis.keys("cache:test:*")
    assert len(keys) == 1

    key = keys[0]
    cached = await test_redis.get(key)
    assert cached == "__NULL__"


async def test_cache_ttl(test_redis):
    async def test_func(x: int, y: int) -> int:
        return x + y

    decorated = cache(ttl=1, prefix="test")(test_func)

    await decorated(2, 3)

    keys = await test_redis.keys("cache:test:*")
    assert len(keys) == 1

    await asyncio.sleep(1.5)

    keys = await test_redis.keys("cache:test:*")
    assert len(keys) == 0


async def test_cache_custom_json_encoder():
    data = {
        "dt": datetime(2026, 7, 3, 12, 0, 0),
        "dec": Decimal("10.5"),
        "hex": b"deadbeef",
    }

    json_str = json.dumps(data, cls=CustomJSONEncoder)
    loaded = json.loads(json_str)

    assert loaded["dt"] == "2026-07-03T12:00:00"
    assert loaded["dec"] == 10.5


async def test_cache_sync_function_error():
    def sync_func():
        return 42

    with pytest.raises(TypeError) as excinfo:
        cache(ttl=60)(sync_func)

    assert "sync" in str(excinfo.value)


async def test_cache_redis_error(test_redis):
    async def test_func(x: int, y: int) -> int:
        return x + y

    decorated = cache(ttl=60, prefix="test")(test_func)

    await test_redis.flushall()

    result = await decorated(2, 3)
    assert result == 5


async def test_invalidate_cache_by_prefix(test_redis):
    async def test_func(x: int, y: int) -> int:
        return x + y

    decorated_user = cache(ttl=60, prefix="user")(test_func)
    decorated_admin = cache(ttl=60, prefix="admin")(test_func)

    await decorated_user(1, 2)
    await decorated_admin(3, 4)

    user_keys = await test_redis.keys("cache:user:*")
    admin_keys = await test_redis.keys("cache:admin:*")
    assert len(user_keys) == 1
    assert len(admin_keys) == 1

    deleted = await invalidate_cache(prefix="user")
    assert deleted == 1

    user_keys = await test_redis.keys("cache:user:*")
    admin_keys = await test_redis.keys("cache:admin:*")
    assert len(user_keys) == 0
    assert len(admin_keys) == 1


async def test_invalidate_cache_all(test_redis):
    async def test_func(x: int, y: int) -> int:
        return x + y

    decorated = cache(ttl=60, prefix="test")(test_func)

    await decorated(1, 2)
    await decorated(3, 4)

    keys_before = await test_redis.keys("cache:*")
    assert len(keys_before) == 2

    deleted = await invalidate_cache()
    assert deleted == 2

    keys_after = await test_redis.keys("cache:*")
    assert len(keys_after) == 0


async def test_invalidate_cache_timeout(test_redis):
    async def test_func(x: int, y: int) -> int:
        return x + y

    for i in range(5):
        decorated = cache(ttl=60, prefix=f"test{i}")(test_func)
        await decorated(i, i + 1)

    async def slow_scan(*args, **kwargs):
        await asyncio.sleep(1)
        return 0, []

    with patch("src.app.utils.cache.redis_client.scan", side_effect=slow_scan):
        deleted = await invalidate_cache(prefix="test1")
        assert deleted == 0


async def test_cache_key_generation(test_redis):
    async def func(a: int, b: int) -> int:
        return a + b

    decorated = cache(ttl=60, prefix="test")(func)

    await decorated(1, 2)
    await decorated(1, 2)

    keys = await test_redis.keys("cache:test:*")
    assert len(keys) == 1


async def test_cache_key_with_kwargs(test_redis):
    async def func(a: int, b: int) -> int:
        return a + b

    decorated = cache(ttl=60, prefix="test")(func)

    await decorated(a=1, b=2)
    await decorated(b=2, a=1)

    keys = await test_redis.keys("cache:test:*")
    assert len(keys) == 1


async def test_cache_key_for_method(test_redis):
    class TestClass:
        async def method(self, x: int) -> int:
            return x * 2

    obj = TestClass()
    decorated = cache(ttl=60, prefix="test")(obj.method)

    await decorated(10)
    await decorated(10)

    keys = await test_redis.keys("cache:test:*")
    assert len(keys) == 1


async def test_cache_integration(test_redis):
    async def test_func(x: int, y: int) -> int:
        return x + y

    decorated = cache(ttl=60, prefix="test")(test_func)

    result1 = await decorated(5, 7)
    assert result1 == 12

    keys = await test_redis.keys("cache:test:*")
    assert len(keys) == 1

    result2 = await decorated(5, 7)
    assert result2 == 12

    await invalidate_cache(prefix="test")

    keys = await test_redis.keys("cache:test:*")
    assert len(keys) == 0

    result3 = await decorated(5, 7)
    assert result3 == 12
