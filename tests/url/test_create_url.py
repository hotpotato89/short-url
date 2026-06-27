from httpx import AsyncClient
import pytest
from fastapi import status

from src.app.schemas.short_url import UrlResponse
from src.app.schemas.token import TokenInfo


async def test_create_url_unauthorized(client: AsyncClient) -> None:
    resp = await client.post("/url", json={"original_url": "https://google.com"})

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


async def test_create_url(client: AsyncClient, fake_user2) -> None:
    await client.post(
        "/auth/register",
        json={
            "email": fake_user2.email,
            "password": fake_user2.password.get_secret_value(),
        },
    )
    login_resp = await client.post(
        "/auth/login",
        json={
            "email": fake_user2.email,
            "password": fake_user2.password.get_secret_value(),
        },
    )

    login_data = TokenInfo(**login_resp.json())

    assert login_resp.status_code == status.HTTP_200_OK

    url_resp = await client.post(
        "/url",
        json={"original_url": "https://google.com"},
        headers={"Authorization": f"Bearer {login_data.access_token}"},
    )

    url_data = UrlResponse(**url_resp.json())

    assert url_resp.status_code == status.HTTP_200_OK
    assert hasattr(url_data, "original_url")
    assert hasattr(url_data, "slug")
    assert hasattr(url_data, "created_at")


async def test_url_create_invalid(client: AsyncClient, fake_user2) -> None:
    await client.post(
        "/auth/register",
        json={
            "email": fake_user2.email,
            "password": fake_user2.password.get_secret_value(),
        },
    )

    login_resp = await client.post(
        "/auth/login",
        json={
            "email": fake_user2.email,
            "password": fake_user2.password.get_secret_value(),
        },
    )

    login_data = TokenInfo(**login_resp.json())

    resp = await client.post(
        "/url",
        json={"original_url": "invalid-url"},
        headers={"Authorization": f"Bearer {login_data.access_token}"},
    )

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
