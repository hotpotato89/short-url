from datetime import datetime

from pydantic import HttpUrl, BaseModel, Field


class UrlCreate(BaseModel):
    original_url: HttpUrl = Field(
        ..., max_length=2048, description="Original url to shorten"
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

    model_config = {"from_attributes": True}
