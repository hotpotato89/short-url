from sqlalchemy.orm import DeclarativeBase

from src.app.models.mixins import IdPkMixin, TimestampMixin


class NoIdBase(DeclarativeBase):
    pass


class Base(NoIdBase, IdPkMixin):
    pass


class BaseTimestamped(Base, TimestampMixin):
    pass
