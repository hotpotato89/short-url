import pytest
from fastapi import status
from httpx import AsyncClient


async def test_stats_unauthorized(client: AsyncClient):
    response = await client.get("/url/test/stats")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_stats_owner_can_view(client: AsyncClient, auth_tokens, mock_click_stats):
    create_response = await client.post(
        "/url",
        json={"original_url": "https://example.com"},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert create_response.status_code == status.HTTP_200_OK

    data = create_response.json()
    slug = data["slug"]

    stats_response = await client.get(
        f"/url/{slug}/stats",
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert stats_response.status_code == status.HTTP_200_OK


async def test_stats_admin_can_view_any(client: AsyncClient, auth_tokens, admin_tokens, mock_click_stats):
    create_response = await client.post(
        "/url",
        json={"original_url": "https://example.com"},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert create_response.status_code == status.HTTP_200_OK

    data = create_response.json()
    slug = data["slug"]

    stats_response = await client.get(
        f"/url/{slug}/stats",
        headers={"Authorization": f"Bearer {admin_tokens.access_token}"},
    )
    assert stats_response.status_code == status.HTTP_200_OK


async def test_stats_other_user_cannot_view(client: AsyncClient, auth_tokens, auth_tokens2):
    create_response = await client.post(
        "/url",
        json={"original_url": "https://example.com"},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert create_response.status_code == status.HTTP_200_OK

    data = create_response.json()
    slug = data["slug"]

    stats_response = await client.get(
        f"/url/{slug}/stats",
        headers={"Authorization": f"Bearer {auth_tokens2.access_token}"},
    )
    assert stats_response.status_code == status.HTTP_403_FORBIDDEN


async def test_stats_not_found(client: AsyncClient, auth_tokens):
    response = await client.get(
        "/url/notexist/stats",
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND