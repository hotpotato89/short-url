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


async def test_create_url_ttl_days(client: AsyncClient, fake_user2) -> None:
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

    url_resp = await client.post(
        "/url",
        json={"original_url": "https://google.com", "ttl_days": 7},
        headers={"Authorization": f"Bearer {login_data.access_token}"},
    )

    assert url_resp.status_code == status.HTTP_200_OK
    data = url_resp.json()
    assert "ttl_days" in data
    assert data["ttl_days"] == 7


async def test_create_url_multiple(client: AsyncClient, fake_user2) -> None:
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

    for i in range(5):
        url_resp = await client.post(
            "/url",
            json={"original_url": f"https://example{i}.com"},
            headers={"Authorization": f"Bearer {login_data.access_token}"},
        )
        assert url_resp.status_code == status.HTTP_200_OK


async def test_create_url_with_credits_spend(client: AsyncClient, fake_user2) -> None:
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

    # Проверяем начальный баланс (5 кредитов)
    credits_resp = await client.get(
        "/credits",
        headers={"Authorization": f"Bearer {login_data.access_token}"},
    )
    assert credits_resp.status_code == status.HTTP_200_OK
    assert credits_resp.json()["credits"] == 5

    # Создаём ссылку
    url_resp = await client.post(
        "/url",
        json={"original_url": "https://google.com"},
        headers={"Authorization": f"Bearer {login_data.access_token}"},
    )
    assert url_resp.status_code == status.HTTP_200_OK

    # Проверяем баланс после создания (должен уменьшиться на 1)
    credits_resp = await client.get(
        "/credits",
        headers={"Authorization": f"Bearer {login_data.access_token}"},
    )
    assert credits_resp.json()["credits"] == 4


async def test_create_url_no_credits(client: AsyncClient, fake_user2) -> None:
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

    # Создаём 5 ссылок (все кредиты)
    for i in range(5):
        url_resp = await client.post(
            "/url",
            json={"original_url": f"https://example{i}.com"},
            headers={"Authorization": f"Bearer {login_data.access_token}"},
        )
        assert url_resp.status_code == status.HTTP_200_OK

    # Проверяем баланс (должен быть 0)
    credits_resp = await client.get(
        "/credits",
        headers={"Authorization": f"Bearer {login_data.access_token}"},
    )
    assert credits_resp.json()["credits"] == 0

    # Пытаемся создать 6-ю ссылку (должна упасть с 403)
    url_resp = await client.post(
        "/url",
        json={"original_url": "https://example5.com"},
        headers={"Authorization": f"Bearer {login_data.access_token}"},
    )
    assert url_resp.status_code == status.HTTP_403_FORBIDDEN
    assert "No credits left" in url_resp.text
