from backend.extensions import ma
from backend.models.activations import Activation
from marshmallow import fields, EXCLUDE


class ActivationSchema(ma.SQLAlchemySchema):
    class Meta:

        model = Activation
        ordered = True
        activation_instance = True
        unknown = EXCLUDE

    datetime = fields.DateTime()
    value = fields.Float()

    date = fields.Date()
    name = fields.String()
    status = fields.Boolean()
    manual = fields.Boolean()
    start = fields.Integer()
    end = fields.Integer()
