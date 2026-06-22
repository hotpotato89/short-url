from typing import Dict

import pytest

from src.app.core.exceptions import InvalidTokenError
from src.app.utils.jwt import create_access_token, decode_jwt, _encode_jwt


TEST_EMAIL: str = "test@test.test"
INVALID_TOKEN: str = 'not-a-token'


async def test_create_access_token() -> None:
    token = create_access_token(1, TEST_EMAIL)

    assert isinstance(token, str)
    assert len(token) > 0


async def test_decode_jwt() -> None:
    token = create_access_token(1, TEST_EMAIL)

    token_payload = decode_jwt(token)

    assert isinstance(token_payload, Dict)
    assert token_payload["sub"] == "1"
    assert token_payload["email"] == TEST_EMAIL
    assert token_payload['type'] == 'access'


async def test_decode_jwt_expired() -> None:
    expired_token = _encode_jwt({"test": "1"}, -1)

    with pytest.raises(InvalidTokenError):
        decode_jwt(expired_token)


async def test_decode_jwt_invalid() -> None:
    with pytest.raises(InvalidTokenError):
        decode_jwt(INVALID_TOKEN)
