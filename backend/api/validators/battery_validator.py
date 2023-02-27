from datetime import datetime

from flask_restful import reqparse
from .base import APIArgument

from backend.utils import tznow
from backend.configs import TIMEZONE


def validate_create_battery():

    parser = reqparse.RequestParser(
        argument_class=APIArgument, bundle_errors=True)

    parser.add_argument("building_id", type=int, required=True)
    parser.add_argument("component_id", type=int, required=True)
    parser.add_argument("battery_type", type=str,
                        choices=('PCS', 'UPS'), required=True)

    parser.add_argument("soc_max", type=float, required=True)
    parser.add_argument("soc_min_coef", type=float, required=True)
    parser.add_argument("p_max", type=float, required=True)
    parser.add_argument("p_charge_max", type=float, required=True)
    parser.add_argument("feeder_max", type=float, required=True)
    parser.add_argument("charging_margin", type=float, required=True)

    parser.add_argument("first_charging_end_time", type=int, required=True)
    parser.add_argument("first_charging_start_time", type=int, required=True)
    parser.add_argument("second_charging_start_time", type=int, required=True)
    parser.add_argument("second_charging_end_time", type=int, required=True)

    args = parser.parse_args()

    return args


def validate_edit_battery():

    parser = reqparse.RequestParser(
        argument_class=APIArgument, bundle_errors=True)

    parser.add_argument("building_id", type=int)
    parser.add_argument("component_id", type=int)
    parser.add_argument("battery_type", type=str, choices=('PCS', 'UPS'),)

    parser.add_argument("soc_max", type=float)
    parser.add_argument("soc_min", type=float)
    parser.add_argument("p_max", type=float)
    parser.add_argument("p_charge_max", type=float)
    parser.add_argument("feeder_max", type=float)
    parser.add_argument("charging_margin", type=float)

    parser.add_argument("first_charging_end_time", type=int, required=True)
    parser.add_argument("first_charging_start_time", type=int, required=True)
    parser.add_argument("second_charging_start_time", type=int, required=True)
    parser.add_argument("second_charging_end_time", type=int, required=True)

    args = parser.parse_args()
    args = {k: v for k, v in args.items() if v}

    return args


def validate_delete_battery_loads():
    parser = reqparse.RequestParser(
        argument_class=APIArgument, bundle_errors=True)

    parser.add_argument("component_id", type=int,
                        required=True, location="args")
    parser.add_argument(
        "date",
        type=lambda x: datetime.strptime(x, "%Y-%m-%d"),
        location="args",
        default=tznow(TIMEZONE).date(),
    )

    args = parser.parse_args()

    return args


def validate_put_battery_loads():
    parser = reqparse.RequestParser(
        argument_class=APIArgument, bundle_errors=True)

    parser.add_argument("component_id", type=int, required=True)
    parser.add_argument("load", type=dict, action='append')

    args = parser.parse_args()

    return args
