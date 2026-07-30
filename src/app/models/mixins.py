from sqlalchemy.orm import Mapped, mapped_column

from src.app.models.base import Base


class IdPkMixin(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
