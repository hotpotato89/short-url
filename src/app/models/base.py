from sqlalchemy.orm import DeclarativeBase

from src.app.models.mixins import IdPkMixin, TimestampMixin


class NoIdBase(DeclarativeBase):
    __abstract__ = True


class Base(NoIdBase, IdPkMixin):
    __abstract__ = True


class BaseTimestamped(Base, TimestampMixin):
    __abstract__ = True
