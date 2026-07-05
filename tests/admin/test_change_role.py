import uuid

import pytest
from fastapi import status
from httpx import AsyncClient

from src.app.schemas.token import TokenInfo
from src.app.schemas.user import UserRegister
from src.app.models.user import User


async def test_admin_change_role_success(
    client: AsyncClient,
    admin_tokens: TokenInfo,
    fake_user2: UserRegister,
) -> None:
    register_resp = await client.post(
        "/auth/register",
        json={
            "email": fake_user2.email,
            "password": fake_user2.password.get_secret_value(),
        },
    )
    assert register_resp.status_code == status.HTTP_200_OK
    user_id = register_resp.json()["id"]
    assert register_resp.json()["role"] == "user"

    resp = await client.patch(
        f"/auth/admin/users/{user_id}/role",
        json={"role": "admin"},
        headers={"Authorization": f"Bearer {admin_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["role"] == "admin"


async def test_admin_cannot_change_own_role(
    client: AsyncClient,
    admin_tokens: TokenInfo,
    admin_user: User,
) -> None:
    resp = await client.patch(
        f"/auth/admin/users/{admin_user.id}/role",
        json={"role": "user"},
        headers={"Authorization": f"Bearer {admin_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


async def test_admin_cannot_change_superadmin_role(
    client: AsyncClient,
    admin_tokens: TokenInfo,
    superadmin_user: User,
) -> None:
    resp = await client.patch(
        f"/auth/admin/users/{superadmin_user.id}/role",
        json={"role": "user"},
        headers={"Authorization": f"Bearer {admin_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


async def test_non_admin_cannot_change_role(
    client: AsyncClient,
    auth_tokens: TokenInfo,
) -> None:
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    register_resp = await client.post(
        "/auth/register",
        json={
            "email": unique_email,
            "password": "test123",
        },
    )
    assert register_resp.status_code == status.HTTP_200_OK
    user_id = register_resp.json()["id"]

    resp = await client.patch(
        f"/auth/admin/users/{user_id}/role",
        json={"role": "admin"},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


async def test_change_role_invalid_user(
    client: AsyncClient,
    admin_tokens: TokenInfo,
) -> None:
    resp = await client.patch(
        "/auth/admin/users/99999/role",
        json={"role": "admin"},
        headers={"Authorization": f"Bearer {admin_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


async def test_change_role_invalid_data(
    client: AsyncClient,
    admin_tokens: TokenInfo,
    fake_user2: UserRegister,
) -> None:
    register_resp = await client.post(
        "/auth/register",
        json={
            "email": fake_user2.email,
            "password": fake_user2.password.get_secret_value(),
        },
    )
    user_id = register_resp.json()["id"]

    resp = await client.patch(
        f"/auth/admin/users/{user_id}/role",
        json={"role": "superadmin"},
        headers={"Authorization": f"Bearer {admin_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT