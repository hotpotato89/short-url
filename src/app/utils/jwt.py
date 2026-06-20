from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any

import jwt

from src.app.core.exceptions import InvalidTokenError
from src.app.core.settings import settings


@lru_cache()
def _private_key():
    return settings.jwt.private_key_path.read_text()


@lru_cache()
def _public_key():
    return settings.jwt.public_key_path.read_text()


def create_access_token(user_id: int, email: str) -> str:
    return _encode_jwt(
        {
            "sub": str(user_id),
            "email": email,
        }
    )


def _encode_jwt(
    payload: dict[str, Any], expire_min: int = 15, type: str = "access"
) -> str:
    to_encode = payload.copy()
    iat = datetime.now(timezone.utc)
    exp = iat + timedelta(minutes=expire_min)
    to_encode["iat"] = iat
    to_encode["exp"] = exp
    to_encode["type"] = type

    return jwt.encode(to_encode, _private_key(), algorithm="RS256")


def decode_jwt(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            _public_key(),
            algorithms=["RS256"],
            options={"verify_signature": True},
        )
    except jwt.exceptions.DecodeError:
        raise InvalidTokenError("Invalid token")
    except jwt.exceptions.ExpiredSignatureError:
        raise InvalidTokenError("Token has expired")
