import json
from http import HTTPStatus

from backend.api import check_request_credentials
from backend.configs import TIMEZONE
from backend.extensions import redis
from backend.extensions.blueprints import alarm
from backend.models import Action, Alarm, Program
from backend.serializers import AlarmSchema
from backend.tasks.utils import calculate_pcs_battery_consumption
from backend.utils import tznow
from dateutil import tz
from flask import abort, jsonify, request
from backend.database import session

from backend.api.validators import (
    validate_retrieve_alarm_content,
    validate_get_alarm_status,
    validate_change_alarm_status,
    validate_get_alarm_history,
)

tzfile = tz.gettz(TIMEZONE)


@alarm.route("/status", methods=["GET"])
def get_alarm_status():

    if not check_request_credentials(request, require_admin_privilege=True):
        return abort(HTTPStatus.UNAUTHORIZED)

    params = validate_get_alarm_status()
    if not redis.exists("need-update"):
        return jsonify({"status": 0}), HTTPStatus.OK

    need_update_values = json.loads(redis.get("need-update"))
    return (
        jsonify({"status": need_update_values.get(
            f"{params['battery_id']}", 0)}),
        HTTPStatus.OK,
    )


@alarm.route("/content", methods=["GET"])
def get_alarm_content():

    if not check_request_credentials(request, require_admin_privilege=True):
        return abort(HTTPStatus.UNAUTHORIZED)

    params = validate_retrieve_alarm_content()

    alarm_obj = Alarm.get(id=params["alarm_id"])
    return AlarmSchema().dump(alarm_obj), HTTPStatus.OK


@alarm.route("/management", methods=["POST"])
def alarm_accept():

    if not check_request_credentials(request, require_admin_privilege=True):
        return abort(HTTPStatus.UNAUTHORIZED)

    params = validate_change_alarm_status()

    alarm_obj = Alarm.get_by(id=params.alarm_id)
    alarm_obj.action = (
        Action.accept if params["decision"] == "accept" else Action.reject
    )
    alarm_obj.clear_time = tznow(TIMEZONE)
    alarm_obj.save(commit=True)

    alarm_status = (
        json.loads(redis.get("need-update")
                   ) if redis.exists("need-update") else {}
    )
    alarm_status[f"{alarm_obj.battery_id}"] = 0
    redis.set("need-update", json.dumps(alarm_status))

    if params["decision"] == "accept":
        pass
        # calculate_pcs_battery_consumption()

    return (""), HTTPStatus.OK


@alarm.route("/history", methods=["GET"])
def alarm_history():

    if not check_request_credentials(request, require_admin_privilege=False):
        return abort(HTTPStatus.UNAUTHORIZED)

    data = validate_get_alarm_history()
    alarams = (session.query(Alarm, Program.name)
               .filter(Alarm.date >= data["start"],
                       Alarm.date <= data["end"],
                       Alarm.battery_id == data["battery_id"])
               .filter(Program.name.in_(data["programs"]))
               .join(Program, Alarm.program_id == Program.id)
               .order_by(Alarm.created_at.desc())
               .all()
               )

    result = [{**AlarmSchema().dump(alrm[0]), 'name': alrm[1]}
              for alrm in alarams]
    return jsonify(result=result), HTTPStatus.OK
