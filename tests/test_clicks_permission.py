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
    stats_data = stats_response.json()
    assert "items" in stats_data
    assert "next_cursor" in stats_data
    assert "has_more" in stats_data
    assert "limit" in stats_data
    assert stats_data["limit"] == 10
    assert isinstance(stats_data["items"], list)


async def test_stats_admin_can_view_any(
    client: AsyncClient, auth_tokens, admin_tokens, mock_click_stats
):
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
    stats_data = stats_response.json()
    assert "items" in stats_data
    assert "next_cursor" in stats_data
    assert "has_more" in stats_data


async def test_stats_other_user_cannot_view(
    client: AsyncClient, auth_tokens, auth_tokens2
):
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


async def test_stats_pagination_first_page(client: AsyncClient, auth_tokens):
    create_response = await client.post(
        "/url",
        json={"original_url": "https://example.com"},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert create_response.status_code == status.HTTP_200_OK
    slug = create_response.json()["slug"]

    response = await client.get(
        f"/url/{slug}/stats?limit=5",
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["limit"] == 5
    assert len(data["items"]) <= 5
    assert "next_cursor" in data
    assert "has_more" in data


async def test_stats_pagination_cursor(client: AsyncClient, auth_tokens):
    create_response = await client.post(
        "/url",
        json={"original_url": "https://example.com"},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert create_response.status_code == status.HTTP_200_OK
    slug = create_response.json()["slug"]

    # Первая страница
    response1 = await client.get(
        f"/url/{slug}/stats?limit=5",
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert response1.status_code == status.HTTP_200_OK
    data1 = response1.json()

    # Если есть следующая страница
    if data1["has_more"]:
        cursor = data1["next_cursor"]
        response2 = await client.get(
            f"/url/{slug}/stats?limit=5&cursor={cursor}",
            headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
        )
        assert response2.status_code == status.HTTP_200_OK
        data2 = response2.json()
        assert len(data2["items"]) <= 5
        # ID на второй странице должны быть меньше, чем на первой
        if data1["items"] and data2["items"]:
            assert data2["items"][0]["id"] < data1["items"][-1]["id"]


async def test_stats_pagination_invalid_cursor(client: AsyncClient, auth_tokens):
    create_response = await client.post(
        "/url",
        json={"original_url": "https://example.com"},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert create_response.status_code == status.HTTP_200_OK
    slug = create_response.json()["slug"]

    response = await client.get(
        f"/url/{slug}/stats?limit=5&cursor=abc",
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_stats_pagination_limit_validation(client: AsyncClient, auth_tokens):
    create_response = await client.post(
        "/url",
        json={"original_url": "https://example.com"},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert create_response.status_code == status.HTTP_200_OK
    slug = create_response.json()["slug"]

    # Лимит больше 100
    response = await client.get(
        f"/url/{slug}/stats?limit=200",
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # Лимит меньше 1
    response = await client.get(
        f"/url/{slug}/stats?limit=0",
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
