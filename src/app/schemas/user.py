from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator


class UserRegister(BaseModel):
    email: EmailStr = Field(..., max_length=255, description="User email")
    password: SecretStr = Field(..., min_length=6, description="User password")

    @field_validator("password")
    @classmethod
    def password_validation(cls, v: SecretStr) -> SecretStr:
        password = v.get_secret_value()
        if len(password) < 6:
            raise ValueError("Password's length must be > 6 characters")
        return v


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: SecretStr = Field(..., description="User password")


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime
    role: Literal['user', 'admin']

    model_config = {"from_attributes": True}
