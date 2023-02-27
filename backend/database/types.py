import datetime
import uuid

from sqlalchemy import schema, types
from sqlalchemy.dialects import sqlite
from sqlalchemy.dialects.postgresql import UUID

from backend.extensions import db  # isort:skip

# pylint: disable=no-member

# alias common names
BigInteger: types.BigInteger = db.BigInteger().with_variant(sqlite.INTEGER(), "sqlite")
Boolean: types.Boolean = db.Boolean
Date: types.Date = db.Date
Enum: types.Enum = db.Enum
Float: types.Float = db.Float
ForeignKey: schema.ForeignKey = db.ForeignKey
Integer: types.Integer = db.Integer
Interval: types.Interval = db.Interval
Numeric: types.Numeric = db.Numeric
SmallInteger: types.SmallInteger = db.SmallInteger
String: types.String = db.String
Text: types.Text = db.Text
DateTime: types.DateTime = db.DateTime
Time: types.Time = db.Time


# pylint: enable=no-member

class GUID(types.TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses CHAR(32), storing as stringified hex values.

    Reference
    ---------
    [1] https://docs.sqlalchemy.org/en/14/core/custom_types.html#backend-agnostic-guid-type
    """

    impl = types.CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(types.CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value
