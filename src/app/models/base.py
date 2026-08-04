from sqlalchemy.orm import DeclarativeBase

from src.app.models.mixins import IdPkMixin, TimestampMixin


class Base(DeclarativeBase, IdPkMixin):
    pass


class BaseTimestamped(Base, TimestampMixin):
    pass
