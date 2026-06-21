import pytest
import httpx

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

    assert resp.status_code == 200
    assert data.email == fake_user.email
    assert hasattr(data, "created_at")
    assert hasattr(data, "id")
