import pytest

from src.app.utils.retry import retry


class CustomTestError(Exception):
    pass


class CustomTestErrorExtra(Exception):
    pass


async def test_retry_success() -> None:
    attempts = 0

    @retry(CustomTestError)
    async def func():
        nonlocal attempts
        attempts += 1

        if attempts < 2:
            raise CustomTestError("Failed")
        return "success"

    result = await func()

    assert result == "success"
    assert attempts == 2


async def test_retry_fail() -> None:
    @retry(CustomTestError)
    async def func() -> None:
        raise CustomTestError("Always fail")

    with pytest.raises(CustomTestError):
        await func()


async def test_retry_uninspected() -> None:
    @retry(CustomTestError)
    async def func() -> None:
        raise CustomTestErrorExtra("Extra fail")

    with pytest.raises(CustomTestErrorExtra):
        await func()
