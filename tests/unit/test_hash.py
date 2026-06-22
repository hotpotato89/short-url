import pytest

from src.app.utils.hash import hash_password, verify_password


TEST_PASSWORD: str = 'very-strong-password'


async def test_hash_password() -> None:
    password_hash = hash_password(TEST_PASSWORD)

    assert isinstance(password_hash, str)
    assert len(password_hash) > 0


async def test_hash_password_empty() -> None:
    password_hash = hash_password('')

    assert isinstance(password_hash, str)
    assert len(password_hash) > 0


async def test_hash_password_salt() -> None:
    password_hash1 = hash_password(TEST_PASSWORD)
    password_hash2 = hash_password(TEST_PASSWORD)

    assert password_hash1 != password_hash2


async def test_verify_password() -> None:
    password_hash = hash_password(TEST_PASSWORD)

    assert verify_password(TEST_PASSWORD, password_hash)


async def test_verify_password_wrong() -> None:
    password_hash = hash_password(TEST_PASSWORD)

    assert not verify_password('wrong-password', password_hash)
