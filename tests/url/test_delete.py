from httpx import AsyncClient
import pytest
from fastapi import status

from src.app.schemas.token import TokenInfo


async def test_delete_slug(client: AsyncClient, auth_tokens: TokenInfo) -> None:
    create_resp = await client.post(
        "/url",
        json={"original_url": "https://google.com"},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    slug = create_resp.json()["slug"]

    assert create_resp.status_code == status.HTTP_200_OK

    delete_resp = await client.delete(
        f"/url/{slug}", headers={"Authorization": f"Bearer {auth_tokens.access_token}"}
    )

    assert delete_resp.status_code == status.HTTP_204_NO_CONTENT


async def test_delete_slug_unauthorize(
    client: AsyncClient, auth_tokens: TokenInfo
) -> None:
    create_resp = await client.post(
        "/url",
        json={"original_url": "https://google.com"},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    slug = create_resp.json()["slug"]

    assert create_resp.status_code == status.HTTP_200_OK

    delete_resp = await client.delete(f"/url/{slug}")

    assert delete_resp.status_code == status.HTTP_401_UNAUTHORIZED


async def test_delete_slug_permission_denied(
    client: AsyncClient, auth_tokens: TokenInfo, auth_tokens2: TokenInfo
) -> None:
    create_resp = await client.post(
        "/url",
        json={"original_url": "https://google.com"},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    slug = create_resp.json()["slug"]

    assert create_resp.status_code == status.HTTP_200_OK

    delete_resp = await client.delete(
        f"/url/{slug}", headers={"Authorization": f"Bearer {auth_tokens2.access_token}"}
    )

    assert delete_resp.status_code == status.HTTP_403_FORBIDDEN


async def test_delete_slug_not_found(
    client: AsyncClient, auth_tokens: TokenInfo
) -> None:
    delete_resp = await client.delete(
        "/url/nonexistent",
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )

    assert delete_resp.status_code == status.HTTP_404_NOT_FOUND
