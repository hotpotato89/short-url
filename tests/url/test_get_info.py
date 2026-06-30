from unittest.mock import patch, PropertyMock
from fastapi import status
from httpx import AsyncClient

from src.app.models.short_url import ShortUrl
from src.app.schemas.token import TokenInfo


async def test_get_url_info_owner(client: AsyncClient, auth_tokens: TokenInfo):
    create_resp = await client.post(
        "/url",
        json={"original_url": "https://example.com"},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    slug = create_resp.json()["slug"]

    resp = await client.get(
        f"/url/{slug}/info",
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["slug"] == slug


async def test_get_url_info_admin_gets_other_user_url(
    client: AsyncClient,
    auth_tokens: TokenInfo,
    admin_tokens: TokenInfo,
):
    """Админ может получить информацию о чужой ссылке."""
    create_resp = await client.post(
        "/url",
        json={"original_url": "https://example.com"},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    slug = create_resp.json()["slug"]

    resp = await client.get(
        f"/url/{slug}/info",
        headers={"Authorization": f"Bearer {admin_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["slug"] == slug


async def test_get_url_info_admin(client: AsyncClient, admin_tokens: TokenInfo):
    create_resp = await client.post(
        "/url",
        json={"original_url": "https://example.com"},
        headers={"Authorization": f"Bearer {admin_tokens.access_token}"},
    )
    slug = create_resp.json()["slug"]

    resp = await client.get(
        f"/url/{slug}/info",
        headers={"Authorization": f"Bearer {admin_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["slug"] == slug


async def test_get_url_info_other_user(
    client: AsyncClient,
    auth_tokens: TokenInfo,
    auth_tokens2: TokenInfo,
):
    create_resp = await client.post(
        "/url",
        json={"original_url": "https://example.com"},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    slug = create_resp.json()["slug"]

    resp = await client.get(
        f"/url/{slug}/info",
        headers={"Authorization": f"Bearer {auth_tokens2.access_token}"},
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


async def test_get_url_info_not_found(client: AsyncClient, auth_tokens: TokenInfo):
    resp = await client.get(
        "/url/notexist/info",
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


async def test_get_url_info_unauthorized(client: AsyncClient):
    resp = await client.get("/url/test/info")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_url_info_invalid_slug(client: AsyncClient, auth_tokens: TokenInfo):
    invalid_slug = "verylong" * 21
    resp = await client.get(
        f"/url/{invalid_slug}/info",
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_get_url_info_expired(
    client: AsyncClient,
    auth_tokens: TokenInfo,
):
    create_resp = await client.post(
        "/url",
        json={"original_url": "https://example.com"},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    slug = create_resp.json()["slug"]

    with patch.object(
        ShortUrl, "is_expired", new_callable=PropertyMock, return_value=True
    ):
        resp = await client.get(
            f"/url/{slug}/info",
            headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
        )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["is_expired"] is True
