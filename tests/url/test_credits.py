from httpx import AsyncClient
import pytest
from fastapi import status

from src.app.schemas.token import TokenInfo


async def test_get_credits_unauthorized(client: AsyncClient) -> None:
    """Без токена — 401"""
    resp = await client.get("/credits")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_credits_authorized(
    client: AsyncClient, auth_tokens: TokenInfo
) -> None:
    """С токеном — возвращает баланс"""
    resp = await client.get(
        "/credits",
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert "credits" in data
    assert data["credits"] == 5


async def test_credits_decrease_after_create_url(
    client: AsyncClient,
    auth_tokens: TokenInfo,
) -> None:
    """После создания ссылки кредит списывается"""
    # Проверяем начальный баланс
    resp = await client.get(
        "/credits",
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert resp.json()["credits"] == 5

    # Создаём ссылку
    url_resp = await client.post(
        "/url",
        json={"original_url": "https://google.com"},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert url_resp.status_code == status.HTTP_200_OK

    # Проверяем баланс после создания (уменьшился на 1)
    resp = await client.get(
        "/credits",
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert resp.json()["credits"] == 4


async def test_credits_blocked_at_zero(
    client: AsyncClient,
    auth_tokens: TokenInfo,
) -> None:
    """При 0 кредитах создание ссылки запрещено"""
    # Создаём 5 ссылок (все кредиты)
    for i in range(5):
        url_resp = await client.post(
            "/url",
            json={"original_url": f"https://example{i}.com"},
            headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
        )
        assert url_resp.status_code == status.HTTP_200_OK

    # Проверяем баланс (должен быть 0)
    resp = await client.get(
        "/credits",
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert resp.json()["credits"] == 0

    # Пытаемся создать 6-ю ссылку (должна упасть с 403)
    url_resp = await client.post(
        "/url",
        json={"original_url": "https://example5.com"},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert url_resp.status_code == status.HTTP_403_FORBIDDEN
    assert "No credits left" in url_resp.text


async def test_different_users_separate_credits(
    client: AsyncClient,
    auth_tokens: TokenInfo,
    auth_tokens2: TokenInfo,
) -> None:
    """У разных пользователей независимые балансы"""
    # Проверяем начальные балансы (оба по 5)
    resp1 = await client.get(
        "/credits",
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    resp2 = await client.get(
        "/credits",
        headers={"Authorization": f"Bearer {auth_tokens2.access_token}"},
    )
    assert resp1.json()["credits"] == 5
    assert resp2.json()["credits"] == 5

    # Первый создаёт ссылку
    url_resp = await client.post(
        "/url",
        json={"original_url": "https://google.com"},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert url_resp.status_code == status.HTTP_200_OK

    # У первого баланс уменьшился, у второго нет
    resp1 = await client.get(
        "/credits",
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    resp2 = await client.get(
        "/credits",
        headers={"Authorization": f"Bearer {auth_tokens2.access_token}"},
    )
    assert resp1.json()["credits"] == 4
    assert resp2.json()["credits"] == 5
