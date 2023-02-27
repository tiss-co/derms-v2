from backend.extensions import ma
from backend.models.load import Load, ManualLoad
from marshmallow import EXCLUDE, fields, validate

DEFAULT_DATE_FORMAT = r"%Y-%m-%d"
DEFAULT_DATETIME_FORMAT = r"%Y-%m-%dT%H:%M:%S"


class LoadModelSchema(ma.SQLAlchemySchema):
    """The LoadModel schema."""

    class Meta:
        """Metaclass for the LoadModelSchema."""

        ordered = True
        unknown = EXCLUDE

    datetime = fields.DateTime(required=True, format=DEFAULT_DATETIME_FORMAT)
    value = fields.Float(required=True, validate=validate.Range(min=0, min_inclusive=True))


class LoadSchema(LoadModelSchema):
    """The Load schema"""

    class Meta:
        """Meta class for the LoadSchema"""

        ordered = True
        unknown = EXCLUDE
        model = Load
        load_instance = True


class ManualLoadSchema(LoadModelSchema):
    """The Manual Load schema"""

    class Meta:
        """Meta class for the ManualLoadSchema"""

        ordered = True
        unknown = EXCLUDE
        model = ManualLoad
        load_instance = True
