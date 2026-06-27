from datetime import datetime

from pydantic import HttpUrl, BaseModel, Field


class UrlCreate(BaseModel):
    original_url: HttpUrl = Field(
        ..., max_length=2048, description="Original url to shorten"
    )

    ttl_days: int | None = Field(
        None, ge=1, le=365, description='TTL in days'
    )


class UrlEdit(BaseModel):
    slug: str = Field(
        ..., min_length=3, max_length=20, description="You can edit only slug"
    )


class UrlResponse(BaseModel):
    id: int
    original_url: str
    slug: str
    clicks: int
    created_at: datetime
    expires_at: datetime
    is_expired: bool

    model_config = {"from_attributes": True}
