import pytest
from fastapi import status

from src.app.schemas.token import TokenInfo


async def test_login(client, fake_user2) -> None:
    fake = {
        "email": fake_user2.email,
        "password": fake_user2.password.get_secret_value(),
    }
    await client.post("/auth/register", json=fake)
    resp = await client.post("/auth/login", json=fake)

    data = TokenInfo(**resp.json())

    assert resp.status_code == status.HTTP_200_OK
    assert hasattr(data, "access_token")
    assert hasattr(data, "refresh_token")
    assert len(data.access_token) > 0
    if data.refresh_token:
        assert len(data.refresh_token) > 0


async def test_login_invalid(client) -> None:
    resp = await client.post("/auth/login", json={})

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_login_invalid_credentials(client, fake_user2) -> None:
    fake = {
        "email": fake_user2.email,
        "password": fake_user2.password.get_secret_value(),
    }
    resp = await client.post("/auth/login", json=fake)

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
