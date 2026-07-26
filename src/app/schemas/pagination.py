from collections.abc import Sequence
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class CursorPaginationResponse[T](BaseModel):
    items: Sequence[T]
    next_cursor: int | None
    limit: int
    has_more: bool

    model_config = {"from_attributes": True}
