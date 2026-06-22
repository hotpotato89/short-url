import pytest
from httpx import AsyncClient
from fastapi import status


async def test_edit_slug(client: AsyncClient, auth_token: str) -> None:
    create_resp = await client.post(
        "/url",
        json={"original_url": "https://google.com"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert create_resp.status_code == status.HTTP_200_OK

    slug = create_resp.json()["slug"]

    edit_resp = await client.put(
        f"/url/{slug}",
        json={"slug": "google"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert edit_resp.status_code == status.HTTP_200_OK

    redirect_resp = await client.get("/url/google", follow_redirects=False)

    assert redirect_resp.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert redirect_resp.headers["Location"] == "https://google.com/"


async def test_edit_slug_unauthorized(client: AsyncClient, auth_token: str) -> None:
    create_resp = await client.post(
        "/url",
        json={"original_url": "https://google.com"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert create_resp.status_code == status.HTTP_200_OK

    slug = create_resp.json()["slug"]

    edit_resp = await client.put(
        f"/url/{slug}",
        json={"slug": "google"},
    )

    assert edit_resp.status_code == status.HTTP_401_UNAUTHORIZED


async def test_edit_slug_conflict(client: AsyncClient, auth_token: str) -> None:
    create_resp1 = await client.post(
        "/url",
        json={"original_url": "https://google.com"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert create_resp1.status_code == status.HTTP_200_OK

    slug1 = create_resp1.json()["slug"]

    create_resp2 = await client.post(
        "/url",
        json={"original_url": "https://google.com"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert create_resp2.status_code == status.HTTP_200_OK

    slug2 = create_resp2.json()["slug"]

    edit_resp = await client.put(
        f"/url/{slug2}",
        json={"slug": slug1},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert edit_resp.status_code == status.HTTP_409_CONFLICT


async def test_edit_slug_permission_denied(
    client: AsyncClient, auth_token: str, auth_token2: str
) -> None:
    create_resp = await client.post(
        "/url",
        json={"original_url": "https://google.com"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    slug = create_resp.json()["slug"]

    assert create_resp.status_code == status.HTTP_200_OK

    edit_resp = await client.put(
        f"/url/{slug}",
        json={"slug": "google"},
        headers={"Authorization": f"Bearer {auth_token2}"},
    )

    assert edit_resp.status_code == status.HTTP_403_FORBIDDEN


async def test_edit_slug_invalid(client: AsyncClient, auth_token: str) -> None:
    create_resp = await client.post(
        "/url",
        json={"original_url": "https://google.com"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    slug = create_resp.json()["slug"]

    assert create_resp.status_code == status.HTTP_200_OK

    invalid_slug = "very_long" * 21  # max = 20

    edit_resp = await client.put(
        f"/url/{slug}",
        json={"slug": invalid_slug},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert edit_resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
