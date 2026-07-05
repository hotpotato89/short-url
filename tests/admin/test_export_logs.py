import pytest
from httpx import AsyncClient

from src.app.schemas.token import TokenInfo


async def test_get_export_logs_denied_for_user(
    client: AsyncClient,
    auth_tokens: TokenInfo,
):
    resp = await client.get(
        "/url/admin/export-logs",
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert resp.status_code == 403


async def test_get_export_logs_denied_for_regular_admin(
    client: AsyncClient,
    admin_tokens: TokenInfo,
):
    resp = await client.get(
        "/url/admin/export-logs",
        headers={"Authorization": f"Bearer {admin_tokens.access_token}"},
    )
    assert resp.status_code == 403


async def test_get_export_logs_as_superadmin(
    client: AsyncClient,
    superadmin_tokens: TokenInfo,
):
    resp = await client.get(
        "/url/admin/export-logs",
        headers={"Authorization": f"Bearer {superadmin_tokens.access_token}"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


async def test_export_logs_limit(
    client: AsyncClient,
    superadmin_tokens: TokenInfo,
):
    resp = await client.get(
        "/url/admin/export-logs?limit=3",
        headers={"Authorization": f"Bearer {superadmin_tokens.access_token}"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) <= 3


async def test_export_logs_denied_without_token(
    client: AsyncClient,
):
    resp = await client.get("/url/admin/export-logs")
    assert resp.status_code == 401
