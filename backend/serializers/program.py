from backend.extensions import ma
from backend.models.programs import Program
from marshmallow import fields, EXCLUDE


class ProgramSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Program
        ordered = True
        load_instance = True
        unknown = EXCLUDE

    id = fields.Integer()
    battery_id = fields.Integer()
    priority = fields.Integer()
    name = fields.String()
    is_global = fields.Boolean()
