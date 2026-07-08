from datetime import datetime, timedelta, timezone
from typing import Dict

import pytest

from src.app.core.exceptions import InvalidTokenError
from src.app.utils.jwt import (
    create_access_token,
    create_refresh_token,
    decode_jwt,
    _encode_jwt,
)

TEST_EMAIL: str = "test@test.test"
INVALID_TOKEN: str = "not-a-token"


async def test_create_access_token() -> None:
    token = create_access_token(1, TEST_EMAIL)
    assert isinstance(token, str)
    assert len(token) > 0


async def test_create_refresh_token() -> None:
    token = create_refresh_token(1, TEST_EMAIL)
    assert isinstance(token, str)
    assert len(token) > 0


async def test_decode_jwt() -> None:
    token = create_access_token(1, TEST_EMAIL)
    token_payload = decode_jwt(token)

    assert isinstance(token_payload, Dict)
    assert token_payload["sub"] == "1"
    assert token_payload["email"] == TEST_EMAIL
    assert token_payload["type"] == "access"
    assert token_payload["role"] == "user"


async def test_decode_jwt_expired() -> None:
    expired_token = _encode_jwt({"sub": "1", "email": TEST_EMAIL}, expire_min=-1)
    with pytest.raises(InvalidTokenError) as exc:
        decode_jwt(expired_token)
    assert "Token has expired" in str(exc.value)


async def test_decode_jwt_invalid() -> None:
    with pytest.raises(InvalidTokenError) as exc:
        decode_jwt(INVALID_TOKEN)
    assert "Invalid token" in str(exc.value)


async def test_decode_jwt_missing_type() -> None:
    import jwt
    from src.app.utils.jwt import _private_key

    payload = {
        "sub": "1",
        "email": TEST_EMAIL,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        "role": "user",
    }
    token = jwt.encode(payload, _private_key(), algorithm="RS256")

    with pytest.raises(InvalidTokenError) as exc:
        decode_jwt(token)
    assert "Missed required claim" in str(exc.value)
    assert "type" in str(exc.value)


async def test_decode_jwt_missing_exp() -> None:
    import jwt
    from src.app.utils.jwt import _private_key

    payload = {
        "sub": "1",
        "email": TEST_EMAIL,
        "iat": datetime.now(timezone.utc),
        "type": "access",
        "role": "user",
    }
    token = jwt.encode(payload, _private_key(), algorithm="RS256")

    with pytest.raises(InvalidTokenError) as exc:
        decode_jwt(token)
    assert "Missed required claim" in str(exc.value)
    assert "exp" in str(exc.value)


async def test_decode_jwt_immature() -> None:
    import jwt
    from src.app.utils.jwt import _private_key

    future_iat = datetime.now(timezone.utc) + timedelta(days=1)
    payload = {
        "sub": "1",
        "email": TEST_EMAIL,
        "iat": future_iat,
        "exp": future_iat + timedelta(minutes=15),
        "type": "access",
        "role": "user",
    }
    token = jwt.encode(payload, _private_key(), algorithm="RS256")

    with pytest.raises(InvalidTokenError) as exc:
        decode_jwt(token)
    assert "Token is not yet valid" in str(exc.value)
