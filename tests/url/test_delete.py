from httpx import AsyncClient
import pytest
from fastapi import status


async def test_delete_slug(client: AsyncClient, auth_token: str) -> None:
    create_resp = await client.post(
        "/url",
        json={"original_url": "https://google.com"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    slug = create_resp.json()["slug"]

    assert create_resp.status_code == status.HTTP_200_OK

    delete_resp = await client.delete(
        f"/url/{slug}", headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert delete_resp.status_code == status.HTTP_204_NO_CONTENT


async def test_delete_slug_unauthorize(client: AsyncClient, auth_token: str) -> None:
    create_resp = await client.post(
        "/url",
        json={"original_url": "https://google.com"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    slug = create_resp.json()["slug"]

    assert create_resp.status_code == status.HTTP_200_OK

    delete_resp = await client.delete(f"/url/{slug}")

    assert delete_resp.status_code == status.HTTP_401_UNAUTHORIZED


async def test_delete_slug_permission_denied(
    client: AsyncClient, auth_token: str, auth_token2: str
) -> None:
    create_resp = await client.post(
        "/url",
        json={"original_url": "https://google.com"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    slug = create_resp.json()["slug"]

    assert create_resp.status_code == status.HTTP_200_OK

    delete_resp = await client.delete(
        f"/url/{slug}", headers={"Authorization": f"Bearer {auth_token2}"}
    )

    assert delete_resp.status_code == status.HTTP_403_FORBIDDEN


async def test_delete_slug_not_found(client: AsyncClient, auth_token: str) -> None:
    delete_resp = await client.delete(
        "/url/nonexistent",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert delete_resp.status_code == status.HTTP_404_NOT_FOUND
