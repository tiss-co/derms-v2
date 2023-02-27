from .base import BaseModel
from .mixins import PrimaryKeyMixin, TimestampMixin


class Model(PrimaryKeyMixin, TimestampMixin, BaseModel):
    """Base model

    Base table class that extends :class:`backend.database.BaseModel` and
    includes a primary key :attr:`id` field along with automatically
    universally unique identifier (UUID) :attr:`uuid`, date-stamped :attr:`created_at`
    and :attr:`updated_at` fields.
    """

    __abstract__: bool = True
    __table_args__: dict = {"extend_existing": True}
    __repr_props__: tuple = ("id", "created_at", "updated_at")
