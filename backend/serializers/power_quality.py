from backend.extensions import ma
from backend.models.power_quality import PowerQuality
from marshmallow import fields, EXCLUDE


class PowerQualitySchema(ma.SQLAlchemySchema):
    """The PowerQuality schema."""

    class Meta:
        """Metaclass for the ResultSchema."""

        model = PowerQuality
        ordered = True
        load_instance = True
        unknown = EXCLUDE

    datetime = fields.DateTime()
    voltage_utility = fields.Float()
    voltage_battery = fields.Float()
    voltage_facility = fields.Float()
    current_utility = fields.Float()
    current_battery = fields.Float()
    current_facility = fields.Float()

