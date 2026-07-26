from collections.abc import Sequence
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class CursorPaginationResponse(BaseModel, Generic[T]):
    items: Sequence[T]
    next_cursor: int | None
    limit: int
    has_more: bool

    model_config = {"from_attributes": True}
