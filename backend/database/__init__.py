# alias common names
from sqlalchemy import CheckConstraint, Index, UniqueConstraint, cast, func, literal_column, orm, text, union
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import validates

from .base import BaseModel
from .column import Column
from .mixins import PrimaryKeyMixin, TimestampMixin
from .model import Model
from .types import (
    GUID,
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Interval,
    Numeric,
    SmallInteger,
    String,
    Text,
    Time,
)

from ..extensions import db  # isort:skip


session: orm.session.Session = db.session
