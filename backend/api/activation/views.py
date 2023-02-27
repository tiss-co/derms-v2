from http import HTTPStatus

from flask import abort, request

from backend.api import check_request_credentials
from backend.configs import TIMEZONE
from backend.database import func, session
from backend.extensions.blueprints import activation
from backend.models import Activation, Program
from backend.serializers import ActivationSchema, ProgramSchema
from backend.tasks.utils import (
    calculate_pcs_battery_consumption,
)
from backend.utils import tznow
from backend.database import session
from backend.api.validators import (
    validate_retrieve_active_programs,
    validate_retrieve_total_active_hours,
    validate_set_program_activation_status,
)
from backend.configs import GLOBAL_PROGRAMS


@activation.route("/status", methods=["GET"])
def get_activated_programs():

    if not check_request_credentials(request, require_admin_privilege=False):
        return abort(HTTPStatus.UNAUTHORIZED)

    params = validate_retrieve_active_programs()

    res = (
        session.query(Activation, Program)
        .filter(Activation.date == params["date"])
        .filter(Program.battery_id == 3)
        .join(Program, Activation.program_id == Program.id)
    )
    response = [
        {
            **ActivationSchema().dump(item.Activation),
            **ProgramSchema().dump(item.Program),
        }
        for item in res
    ]

    return response


@activation.route("/total_activated_hours", methods=["GET"])
def get_total_activation_hours():

    if not check_request_credentials(request, require_admin_privilege=False):
        return abort(HTTPStatus.UNAUTHORIZED)

    params = validate_retrieve_total_active_hours()
    active_programs = (
        session.query(func.sum(Activation.end - Activation.start + 1), Program.name)
        .join(Activation)
        .filter(Program.battery_id == params["battery_id"], Activation.status == True)
        .group_by(Program.name)
        .all()
    )
    json_active_hours = {}
    for program in active_programs:
        json_active_hours[program[1]] = program[0]

    return json_active_hours, HTTPStatus.OK


@activation.route("/set_activation", methods=["POST"])
def set_program_activation_status():

    if not check_request_credentials(request, require_admin_privilege=True):
        return abort(HTTPStatus.UNAUTHORIZED)

    now = tznow(TIMEZONE).date()

    data = validate_set_program_activation_status()

    program_obj = Program.get(id=data["program_id"])
    activation_obj = Activation.get_by(program_id=data["program_id"], date=now)

    activation_obj.is_manual = data["is_manual"]
    activation_obj.save(commit=True)

    if not data["is_manual"]:
        return (""), HTTPStatus.OK

    if program_obj.name not in GLOBAL_PROGRAMS:
        return {
            "message": "Manual parameter can only be set for global programs"
        }, HTTPStatus.BAD_REQUEST

    activation_obj.status = data["status"]

    if data["status"]:
        activation_obj.start = data["activation"]["start"]
        activation_obj.end = data["activation"]["end"]

    activation_obj.save(commit=True)

    # calculate_pcs_battery_consumption()
    return (""), HTTPStatus.OK
