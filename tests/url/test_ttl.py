import pytest
from datetime import datetime, timezone
from fastapi import status
from httpx import AsyncClient
from unittest.mock import patch, PropertyMock

from src.app.models.short_url import ShortUrl
from src.app.schemas.token import TokenInfo


async def test_create_url_without_ttl(
    client: AsyncClient,
    auth_tokens: TokenInfo,
) -> None:
    resp = await client.post(
        "/url",
        json={"original_url": "https://example.com"},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["expires_at"] is None
    assert data["is_expired"] is False


async def test_create_url_with_ttl(
    client: AsyncClient,
    auth_tokens: TokenInfo,
) -> None:
    resp = await client.post(
        "/url",
        json={"original_url": "https://example.com", "ttl_days": 7},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["expires_at"] is not None
    assert data["is_expired"] is False


async def test_create_url_with_ttl_1_day(
    client: AsyncClient,
    auth_tokens: TokenInfo,
) -> None:
    resp = await client.post(
        "/url",
        json={"original_url": "https://example.com", "ttl_days": 1},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["expires_at"] is not None

    expires_at = datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    diff = expires_at - now
    assert 23 <= diff.total_seconds() / 3600 <= 25


async def test_create_url_with_ttl_max(
    client: AsyncClient,
    auth_tokens: TokenInfo,
) -> None:
    resp = await client.post(
        "/url",
        json={"original_url": "https://example.com", "ttl_days": 365},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["expires_at"] is not None


async def test_create_url_with_invalid_ttl(
    client: AsyncClient,
    auth_tokens: TokenInfo,
) -> None:
    resp = await client.post(
        "/url",
        json={"original_url": "https://example.com", "ttl_days": 0},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_create_url_with_ttl_too_high(
    client: AsyncClient,
    auth_tokens: TokenInfo,
) -> None:
    resp = await client.post(
        "/url",
        json={"original_url": "https://example.com", "ttl_days": 400},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_expired_url_returns_404(
    client: AsyncClient,
    auth_tokens: TokenInfo,
) -> None:
    resp = await client.post(
        "/url",
        json={"original_url": "https://example.com", "ttl_days": 1},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    slug = resp.json()["slug"]

    with patch.object(
        ShortUrl, "is_expired", new_callable=PropertyMock, return_value=True
    ):
        redirect_resp = await client.get(f"/url/{slug}")
        assert redirect_resp.status_code == status.HTTP_404_NOT_FOUND


async def test_edit_expired_url(
    client: AsyncClient,
    auth_tokens: TokenInfo,
) -> None:
    resp = await client.post(
        "/url",
        json={"original_url": "https://example.com", "ttl_days": 1},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    slug = resp.json()["slug"]

    with patch.object(
        ShortUrl, "is_expired", new_callable=PropertyMock, return_value=True
    ):
        edit_resp = await client.put(
            f"/url/{slug}",
            json={"slug": "new-slug"},
            headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
        )
        assert edit_resp.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_expired_url(
    client: AsyncClient,
    auth_tokens: TokenInfo,
) -> None:
    resp = await client.post(
        "/url",
        json={"original_url": "https://example.com", "ttl_days": 1},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    slug = resp.json()["slug"]

    with patch.object(
        ShortUrl, "is_expired", new_callable=PropertyMock, return_value=True
    ):
        delete_resp = await client.delete(
            f"/url/{slug}",
            headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
        )
        assert delete_resp.status_code == status.HTTP_404_NOT_FOUND
