import pytest
from fastapi import status
from httpx import AsyncClient

from src.app.schemas.token import TokenInfo


async def test_admin_get_all_users_with_limit(
    client: AsyncClient,
    admin_tokens: TokenInfo,
) -> None:
    resp = await client.get(
        "/auth/admin/users?limit=5",
        headers={"Authorization": f"Bearer {admin_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) <= 5


async def test_admin_get_all_users_default_limit(
    client: AsyncClient,
    admin_tokens: TokenInfo,
) -> None:
    resp = await client.get(
        "/auth/admin/users",
        headers={"Authorization": f"Bearer {admin_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert len(data) <= 100


async def test_admin_get_all_users_invalid_limit(
    client: AsyncClient,
    admin_tokens: TokenInfo,
) -> None:
    resp = await client.get(
        "/auth/admin/users?limit=2000",
        headers={"Authorization": f"Bearer {admin_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
