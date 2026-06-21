import pytest
import httpx
from fastapi import status

from src.app.schemas.user import UserResponse


async def test_register(client, fake_user) -> None:
    resp = await client.post(
        "/auth/register",
        json={
            "email": fake_user.email,
            "password": fake_user.password.get_secret_value(),
        },
    )

    data = UserResponse(**resp.json())

    assert resp.status_code == status.HTTP_200_OK
    assert data.email == fake_user.email
    assert hasattr(data, "created_at")
    assert hasattr(data, "id")


async def test_register_invalid(client) -> None:
    resp = await client.post("/auth/register", json={})

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_register_conflict(client, fake_user) -> None:
    user = {
        "email": fake_user.email,
        "password": fake_user.password.get_secret_value(),
    }
    await client.post("/auth/register", json=user)
    resp = await client.post("/auth/register", json=user)

    assert resp.status_code == status.HTTP_409_CONFLICT
