from backend.extensions import ma
from backend.models.alarms import Alarm
from marshmallow import fields, EXCLUDE, Schema
from marshmallow_enum import EnumField
from backend.models.alarms import Action


class LastUpdateSchema(Schema):
    new_value = fields.String()
    old_value = fields.String()


class StatusSchema(Schema):
    new_value = fields.Boolean()
    old_value = fields.Boolean()


class StartSchema(Schema):
    new_value = fields.Integer()
    old_value = fields.Integer()


class EndSchema(Schema):
    new_value = fields.Integer()
    old_value = fields.Integer()


class ManualSchema(Schema):
    new_value = fields.Boolean()
    old_value = fields.Boolean()


class ContentSchema(Schema):
    """The Content schema."""

    last_update = fields.Nested(LastUpdateSchema)
    status = fields.Nested(StatusSchema)
    start = fields.Nested(StartSchema)
    end = fields.Nested(EndSchema)
    manual = fields.Nested(ManualSchema)


class AlarmSchema(ma.SQLAlchemySchema):
    """The Alarm schema."""

    class Meta:
        """Metaclass for the AlarmSchema."""

        model = Alarm
        ordered = True
        alarm_instance = True
        unknown = EXCLUDE

    date = fields.Date()
    program_name = fields.String()
    content = fields.Nested(ContentSchema)
    receive_time = fields.DateTime()
    clear_time = fields.DateTime()
    action = EnumField(Action)
