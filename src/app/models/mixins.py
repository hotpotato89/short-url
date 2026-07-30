from sqlalchemy.orm import Mapped, mapped_column

from src.app.models.base import Base


class IdPkMixin(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
