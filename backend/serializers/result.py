from backend.extensions import ma
from backend.models.result import Result
from marshmallow import fields, EXCLUDE


class ResultSchema(ma.SQLAlchemySchema):
    """The Result schema."""

    class Meta:
        """Metaclass for the ResultSchema."""

        model = Result
        ordered = True
        load_instance = True
        unknown = EXCLUDE

    datetime = fields.DateTime()
    charging_status = fields.Integer()
    charging_mode = fields.Integer()
    power = fields.Float()
    limited_soc = fields.Float()
    real_soc = fields.Float()
    utility_power = fields.Float()
