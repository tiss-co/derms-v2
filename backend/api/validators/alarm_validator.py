from datetime import datetime

from flask_restful import reqparse
from .base import APIArgument

from backend.utils import tznow
from backend.configs import TIMEZONE


def validate_get_alarm_status():
    parser = reqparse.RequestParser(
        argument_class=APIArgument, bundle_errors=True)

    parser.add_argument("battery_id", type=int, required=True, location="args")
    args = parser.parse_args()

    return args


def validate_retrieve_alarm_content():

    parser = reqparse.RequestParser(
        argument_class=APIArgument, bundle_errors=True)

    parser.add_argument("alarm_id", type=int, required=True, location="args")
    args = parser.parse_args()

    return args


def validate_change_alarm_status():

    parser = reqparse.RequestParser(
        argument_class=APIArgument, bundle_errors=True)

    parser.add_argument("alarm_id", type=int, required=True)
    parser.add_argument(
        "decision", type=str, required=True, choices=("accept", "reject")
    )
    args = parser.parse_args()

    return args


def validate_get_alarm_history():

    parser = reqparse.RequestParser(
        argument_class=APIArgument, bundle_errors=True)

    parser.add_argument("battery_id", type=int, required=True)
    parser.add_argument("programs", type=str, action="append")
    parser.add_argument(
        "start",
        type=lambda x: datetime.strptime(x, "%Y-%m-%d"),
        default=tznow(TIMEZONE).date(),
    )

    parser.add_argument(
        "end",
        type=lambda x: datetime.strptime(x, "%Y-%m-%d"),
        default=tznow(TIMEZONE).date(),
    )

    args = parser.parse_args()

    return args
