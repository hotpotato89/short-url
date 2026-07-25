from pydantic import BaseModel
from typing import Sequence, TypeVar, Generic


T = TypeVar("T")


class CursorPaginationResponse(BaseModel, Generic[T]):
    items: Sequence[T]
    next_cursor: int | None
    limit: int
    has_more: bool

    model_config = {"from_attributes": True}
