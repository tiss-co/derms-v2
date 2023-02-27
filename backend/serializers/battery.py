from marshmallow import EXCLUDE, fields

from backend.extensions import ma
from backend.models.battery import Battery


class BatterySchema(ma.SQLAlchemySchema):
    class Meta:
        model = Battery
        ordered = True
        load_instance = True
        unknown = EXCLUDE

    id = fields.Integer()
    building_id = fields.Integer()
    component_id = fields.Integer()
    p_max = fields.Float()
    battery_type = fields.String()
    soc_max = fields.Float()
    soc_min = fields.Float()
    feeder_max = fields.Float()
    charging_margin = fields.Float()
    first_charging_start_time = fields.Integer()
    first_charging_end_time = fields.Integer()
    second_charging_start_time = fields.Integer()
    second_charging_end_time = fields.Integer()
