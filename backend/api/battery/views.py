from datetime import datetime, time
from http import HTTPStatus
from typing import Tuple
import ast

from backend.api import check_request_credentials
from backend.api.common import get_loads
from backend.configs import TIMEZONE
from backend.database import func
from backend.extensions.blueprints import battery
from backend.models import (
    BatteryDetails,
    Load,
    ManualLoad,
    PowerQuality,
    Result,
    Battery,
)
from backend.serializers import (
    BatteryDetailsSchema,
    PowerQualitySchema,
    ResultSchema,
    BatterySchema,
)
from backend.tasks.utils import calculate_pcs_battery_consumption
from backend.utils import tznow
from dateutil import parser, tz
from flask import abort, jsonify, request
from werkzeug.wrappers import Response
from backend.api.validators import validate_create_battery, validate_edit_battery, validate_delete_battery_loads, validate_put_battery_loads
from backend.database import session

tzfile = tz.gettz(TIMEZONE)


@battery.route("/", methods=["POST"])
def create():

    data = validate_create_battery()
    data["soc_min"] = data["soc_max"] * data["soc_min_coef"]
    del data["soc_min_coef"]

    new_battery = Battery(**data)
    new_battery.save(commit=True)

    return (""), HTTPStatus.CREATED


@battery.route("/<battery_id>", methods=["GET"])
def get(battery_id):

    battery_obj = Battery.get(id=battery_id)
    return BatterySchema().dump(battery_obj), HTTPStatus.OK


@battery.route("/<battery_id>", methods=["PUT"])
def put(battery_id):

    data = validate_edit_battery()

    body = ast.literal_eval(str(data))
    battery_obj = Battery.get(id=battery_id)

    if not battery_obj:
        return (
            jsonify({"status": f"No battery found with id {battery_id}"}),
            HTTPStatus.NOT_FOUND,
        )

    battery_obj.update(**body)
    battery_obj.save(commit=True)

    return (""), HTTPStatus.OK


@battery.route("/<battery_id>", methods=["DELETE"])
def delete(battery_id):

    battery_obj = Battery.get(id=battery_id)
    if not battery_obj:
        return (
            jsonify({"status": f"No battery found with id {battery_id}"}),
            HTTPStatus.NOT_FOUND,
        )
    battery_obj.delete(commit=True)

    return (""), HTTPStatus.OK


@battery.route("/PCS/consumption", methods=["GET"])
def get_pcs_battery_consumption():
    """
    Get the battery consumption of the PCS

    Returns
    -------
    responses: dict
      200:
        description: Dictionary of the PCS battery consumption based on the date parameter
        schema:
          charging_status: array
          charging_mode: array
          power: array
          limited_soc: array
          real_soc: array
          utility_power: array
          last_update: str(datetime)
    """

    if not check_request_credentials(request, require_admin_privilege=False):
        return abort(HTTPStatus.UNAUTHORIZED)  # Authorization failed

    args = request.args
    params = args.to_dict()
    requested_date = params.get("date")
    date = (
        parser.parse(requested_date).date()
        if requested_date
        else tznow(TIMEZONE).date()
    )
    results = (
        Result.filter(func.date(Result.datetime) == date)
        .order_by(Result.datetime)
        .all()
    )
    last_update = [item.updated_at for item in results]

    return jsonify(
        last_update=max(last_update).astimezone(
            tzfile).strftime("%Y-%m-%dT%H:%M:%S")
        if last_update
        else None,
        result=ResultSchema(many=True).dump(results),
    )


@battery.route("/PCS/load", methods=["GET"])
def get_battery_load():
    """
    Get the battery load of the PCS considering date parameter.

    Parameters
    ----------
    date: str(datetime)
        The date of the load to be retrieved. only dates with %Y-%m-%d format are acceptable.

    Returns
    -------
    200: dict
        description: Dictionary of the PCS battery load based on the date parameter
        schema:
            results: 24 array
                datetime: str(datetime)
                value: float
    """

    if not check_request_credentials(request, require_admin_privilege=False):
        return abort(HTTPStatus.UNAUTHORIZED)  # Authorization failed

    args = request.args
    params = args.to_dict()
    requested_date = params.get("date")
    date = (
        parser.parse(requested_date).date()
        if requested_date
        else tznow(TIMEZONE).date()
    )

    results = get_loads(date=date)
    return jsonify(result=results), HTTPStatus.OK


@battery.route("/PCS/details", methods=["GET"])
def get_battery_details():
    """
    Get the battery details
    Returns
    -------
    responses: dict
        200:
            description: Dictionary of the battery details
            schema:
                p_max:
                p_max_charge:
                capacity:
                available_energy:
                state_of_charge:
                remaining_life_cycle:
                state_of_health:
                grid_frequency:
                average_grid_current:
                reactive_power:
                ambient_temperature:
                power_factor:
        404:
            description: Battery details not found
    """

    if not check_request_credentials(request, require_admin_privilege=False):
        return abort(HTTPStatus.UNAUTHORIZED)  # Authorization failed

    current_time = datetime.combine(
        tznow(TIMEZONE).date(), time(tznow(TIMEZONE).hour, 0)
    )
    current_battery_details = BatteryDetails.get_by(datetime=current_time)

    if current_battery_details:
        return (
            jsonify(BatteryDetailsSchema().dump(current_battery_details)),
            HTTPStatus.OK,
        )

    else:
        return jsonify({"status": "No battery details found"}), HTTPStatus.NOT_FOUND


@battery.route("/PCS/voltage_current", methods=["GET"])
def get_voltage_current():
    """
    Get the voltage and current of the PCS considering date parameter.

    Parameters
    ----------
    date: str(datetime)
        The date of the voltage and current to be retrieved. only dates with %Y-%m-%d format are acceptable.

    Returns
    -------
        200:
            description: Dictionary of the PCS voltage and current data
            schema:
                datetime:
                current_battery:
                current_facility:
                current_utility:
                voltage_battery:
                voltage_facility:
                voltage_utility:
        404:
            description: Voltage and current data not found
    """

    if not check_request_credentials(request, require_admin_privilege=False):
        return abort(HTTPStatus.UNAUTHORIZED)  # Authorization failed

    args = request.args
    params = args.to_dict()
    requested_date = params.get("date")
    query_date = (
        parser.parse(requested_date).date()
        if requested_date
        else tznow(TIMEZONE).date()
    )
    results = (
        PowerQuality.filter(func.date(PowerQuality.datetime) == query_date)
        .order_by(PowerQuality.datetime)
        .all()
    )

    if results:
        return jsonify(PowerQualitySchema(many=True).dump(results)), 200
    else:
        return jsonify({"message": "No voltage current data found"}), 404


@battery.route("/PCS/power_flow", methods=["GET"])
def get_power_flow_battery():
    """
    Get the power flow for battery, utility, and facility at each time.

    Returns
    -------
        200:
            description: Dictionary of the power flow
            schema:
                facility_power:
                facility_current:
                utility_power:
                utility_current:
                battery_power:
                battery_current:
                charging_status:
        404:
            description: power flow data not found
    """

    if not check_request_credentials(request, require_admin_privilege=False):
        return abort(HTTPStatus.UNAUTHORIZED)  # Authorization failed

    current_time = datetime.combine(
        tznow(TIMEZONE).date(), time(tznow(TIMEZONE).hour, 0)
    )
    power_quality_result = PowerQuality.get_by(datetime=current_time)
    calculation_result = Result.get_by(datetime=current_time)
    facility_power = Load.get_by(datetime=current_time)

    svg_status = 0
    if calculation_result:
        if calculation_result.charging_status == 1:
            svg_status = 2
        elif calculation_result.charging_status == -1:
            if calculation_result.utility_power == 0:
                svg_status = 3
            else:
                svg_status = 1

    if power_quality_result and calculation_result and facility_power:
        return (
            jsonify(
                {
                    "facility_current": power_quality_result.current_facility
                    if power_quality_result
                    else None,
                    "facility_power": facility_power.value if facility_power else None,
                    "utility_power": calculation_result.utility_power
                    if power_quality_result
                    else None,
                    "utility_current": power_quality_result.current_utility
                    if power_quality_result
                    else None,
                    "battery_power": calculation_result.power
                    if calculation_result
                    else None,
                    "battery_current": power_quality_result.current_battery
                    if power_quality_result
                    else None,
                    "svg_status": svg_status,
                }
            ),
            HTTPStatus.OK,
        )

    else:
        return jsonify({"message": "No power flow data found."}), HTTPStatus.NOT_FOUND


@battery.route("/PCS/load", methods=["PUT"])
def put_battery_loads() -> Tuple[Response, HTTPStatus]:
    """

    Parameters
    ----------
    load: 24 array
        datetime: str(datetime) Only datetime with "%Y-%m-%dT%H:%M:%S" format is acceptable.
        value: float

    """
    if not check_request_credentials(request, require_admin_privilege=True):
        return abort(HTTPStatus.UNAUTHORIZED)

    params = validate_put_battery_loads()

    for load_item in params['load']:
        manual_load_obj = ManualLoad.get_or_create(
            datetime=datetime.strptime(
                load_item["datetime"], '%Y-%m-%dT%H:%M:%S'),
            component_id=params['component_id'])
        manual_load_obj.update(commit=True, value=load_item["value"])

    # calculate_pcs_battery_consumption()
    return jsonify(), HTTPStatus.NO_CONTENT


@battery.route("/PCS/load", methods=["DELETE"])
def delete_battery_load() -> Tuple[Response, HTTPStatus]:

    if not check_request_credentials(request, require_admin_privilege=True):
        return abort(HTTPStatus.UNAUTHORIZED)

    params = validate_delete_battery_loads()

    stmt = ManualLoad.__table__.delete().where(
        ManualLoad.component_id == params['component_id'], func.date(ManualLoad.datetime) == params['date'].date())

    session.execute(statement=stmt)
    session.commit()

    # calculate_pcs_battery_consumption()
    return jsonify(), HTTPStatus.NO_CONTENT
