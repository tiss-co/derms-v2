from flask_restful import reqparse
from .base import APIArgument


def validate_create_program():

    parser = reqparse.RequestParser(
        argument_class=APIArgument, bundle_errors=True)

    parser.add_argument("battery_id", type=int, required=True)

    parser.add_argument("name", type=str, required=True)
    parser.add_argument("priority", type=int, required=True)
    parser.add_argument("is_global", type=bool, required=True)

    args = parser.parse_args()

    return args


def validate_edit_program():

    parser = reqparse.RequestParser(
        argument_class=APIArgument, bundle_errors=True)

    parser.add_argument("battery_id", type=int)

    parser.add_argument("name", type=str)
    parser.add_argument("priority", type=int)
    parser.add_argument("is_global", type=bool)

    args = parser.parse_args()
    args = {k: v for k, v in args.items() if v != None}

    return args
