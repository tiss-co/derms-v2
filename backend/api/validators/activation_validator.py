from datetime import datetime

from flask_restful import reqparse
from .base import APIArgument

from backend.utils import tznow
from backend.configs import TIMEZONE


def validate_retrieve_active_programs():

    parser = reqparse.RequestParser(argument_class=APIArgument, bundle_errors=True)

    parser.add_argument("battery_id", type=int, required=True, location="args")
    parser.add_argument(
        "date",
        type=lambda x: datetime.strptime(x, "%Y-%m-%d"),
        location="args",
        default=tznow(TIMEZONE).date(),
    )

    args = parser.parse_args()

    return args


def validate_retrieve_total_active_hours():

    parser = reqparse.RequestParser(argument_class=APIArgument, bundle_errors=True)

    parser.add_argument("battery_id", type=int, required=True, location="args")
    parser.add_argument(
        "start",
        type=lambda x: datetime.strptime(x, "%Y-%m-%d"),
        location="args",
        default=tznow(TIMEZONE).date(),
    )

    parser.add_argument(
        "end",
        type=lambda x: datetime.strptime(x, "%Y-%m-%d"),
        location="args",
        default=tznow(TIMEZONE).date(),
    )

    args = parser.parse_args()

    return args


def validate_set_program_activation_status():
    root_parser = reqparse.RequestParser(argument_class=APIArgument, bundle_errors=True)

    root_parser.add_argument("program_id", type=int, required=True)
    root_parser.add_argument("is_manual", type=bool, required=True)
    root_parser.add_argument("status", type=bool)
    root_parser.add_argument("activation", type=dict)
    root_args = root_parser.parse_args()

    activation_parser = reqparse.RequestParser(
        argument_class=APIArgument, bundle_errors=True
    )
    activation_parser.add_argument(
        "start",
        type=int,
        location=("activation",),
        required=True if root_args["is_manual"] and root_args["status"] else False,
    )
    activation_parser.add_argument(
        "end",
        type=int,
        location=("activation",),
        required=True if root_args["is_manual"] and root_args["status"] else False,
    )
    activation_args = activation_parser.parse_args(req=root_args)

    return root_args
