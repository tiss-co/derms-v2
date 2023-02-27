from backend.extensions import ma
from backend.models.battery_details import BatteryDetails
from marshmallow import fields, EXCLUDE


class BatteryDetailsSchema(ma.SQLAlchemySchema):
    """The Battery Details schema."""

    class Meta:
        """Metaclass for the BatteryDetails."""

        model = BatteryDetails
        ordered = True
        load_instance = True
        unknown = EXCLUDE

    datetime = fields.DateTime()
    current_status = fields.String()
    p_max = fields.Float()
    p_max_charge = fields.Float()
    capacity = fields.Float()
    available_energy = fields.Float()
    state_of_charge = fields.Float()
    remaining_life_cycle = fields.Float()
    state_of_health = fields.Float()
    grid_frequency = fields.Float()
    average_grid_current = fields.Float()
    reactive_power = fields.Float()
    ambient_temperature = fields.Float()
    power_factor = fields.Float()
