import json
import re
from datetime import datetime, time, timedelta

import numpy as np
from dateutil import parser
from deepdiff import DeepDiff

from backend.api.common import get_loads
from backend.configs import TIMEZONE
from backend.database import func, session
from backend.extensions import redis
from backend.logger import logger
from backend.models import Action, Activation, Alarm, Battery, Program, Result
from backend.modules.derms import PCSBattery, settings
from backend.serializers import ActivationSchema, BatterySchema, ProgramSchema
from backend.utils import tznow


def calculate_pcs_battery_consumption(comp_id: int, battery_id: int) -> None:
    """Calculate battery charge and discharge values

    Based on load values and activated programs

    Raises
    ------
    NotFoundErr:
        No load data found.
    """

    load_consumption = get_loads(tznow(TIMEZONE).date(), comp_id=comp_id)
    load_values = [item["value"] for item in load_consumption]
    load_dict = {k: v for k, v in enumerate(load_values, 1)}

    if load_values:
        program_activation_obj = (
            session.query(Program, Activation)
            .filter(Program.id == Activation.program_id)
            .filter(Program.battery_id == battery_id, Activation.date == tznow(TIMEZONE).date())
            .all()
        )

        program_activation_res = [
            {
                **ActivationSchema().dump(item.Activation),
                **ProgramSchema().dump(item.Program),
            }
            for item in program_activation_obj
        ]

        battery_features = dict(BatterySchema().dump(Battery.get_by(id=battery_id)))
        battery_features["soc_available"] = 1000

        pcs_battery = PCSBattery(load=load_dict, battery_features=battery_features, programs=program_activation_res)

        pcs_battery.calculate_pcs_battery_consumption()

        p_discharge = np.array(list(pcs_battery.model.Pbdch.get_values().values()))
        p_charge = np.array(list(pcs_battery.model.Pbch.get_values().values()))

        charging_status = np.zeros(24, dtype="int32")
        charging_status[p_discharge != 0] = -1
        charging_status[p_charge != 0] = 1
        charging_status = charging_status.tolist()

        power = np.abs((p_charge + p_discharge).round(4)).tolist()
        soc = np.array(list(pcs_battery.model.soc.get_values().values())).round(4).tolist()

        utility_power = [(a * b) + c for a, b, c in zip(charging_status, power, load_values)]

        # Get all the results for today
        today_results = (
            Result.filter(func.date(Result.datetime) == tznow(TIMEZONE).date(), Result.battery_id == battery_id)
            .order_by(Result.datetime)
            .all()
        )

        # Check if is not first time to save results to DB
        if today_results:
            charging_status_old = [rs.charging_status for rs in today_results]
            power_old = [rs.power for rs in today_results]
            soc_old = [rs.soc for rs in today_results]
            utility_power_old = [rs.utility_power for rs in today_results]

            # Update the new calculated results with the previous results
            charging_status[: tznow(TIMEZONE).hour + 1] = charging_status_old[: tznow(TIMEZONE).hour + 1]
            power[: tznow(TIMEZONE).hour + 1] = power_old[: tznow(TIMEZONE).hour + 1]
            soc[: tznow(TIMEZONE).hour + 1] = soc_old[: tznow(TIMEZONE).hour + 1]
            utility_power[: tznow(TIMEZONE).hour + 1] = utility_power_old[: tznow(TIMEZONE).hour + 1]

        # Save results for the first time
        for i in range(24):
            res = Result.get_or_create(
                datetime=datetime.combine(tznow(TIMEZONE).date(), time(i, 0)), battery_id=battery_id
            )
            res.update(
                commit=True,
                charging_status=charging_status[i],
                power=power[i],
                soc=soc[i],
                utility_power=utility_power[i],
            )
    else:
        raise Exception("No load data found")


def get_dict_diff(new_data: dict, old_data: dict):
    """
    Get changes between two dictionaries
    Parameters
    ----------
    new_data: dict
    old_data: dict

    Returns
    -------
    changes: dict
    """

    changes = {}
    excluded_regex = r"'(.*?)'"
    diff = DeepDiff(new_data, old_data)

    for k in diff.get("values_changed", []):
        changes[re.findall(excluded_regex, k)[-1]] = diff["values_changed"][k]

    return changes


def get_list_diff(new_data: list, old_data: list):
    """
    Get changes between two lists
    Parameters
    ----------
    new_data: list
    old_data: list

    Returns
    -------
    changes: dict
    """

    changes = {}
    excluded_regex = r"\[(.*?)\]"
    diff = DeepDiff(new_data, old_data)

    for k in diff.get("values_changed", []):
        changes[int(re.findall(excluded_regex, k)[-1])] = diff["values_changed"][k]

    return changes


def daily_activity_hours() -> list:
    """
    Get daily activation hours
    It tells how many hours of the day the Programs are activated

    Returns
    -------
    activation_mode: list
    """
    activated_programs_results = (
        Activation.filter(func.date(Activation.date) == tznow(TIMEZONE).date()).order_by(Activation.date).all()
    )

    activated_programs = dict()
    for item in activated_programs_results:
        activated_programs[item.name.lower()] = {
            "status": item.status,
            "activation": {"start": item.start, "end": item.end},
        }

    ga_st = int(activated_programs.get("ga", {}).get("activation", {}).get("start") or 0) + 1
    ga_et = int(activated_programs.get("ga", {}).get("activation", {}).get("end") or 0) + 1
    dr_st = int(activated_programs.get("dr", {}).get("activation", {}).get("start") or 0) + 1
    dr_et = int(activated_programs.get("dr", {}).get("activation", {}).get("end") or 0) + 1
    hoep_st = int(activated_programs.get("hoep", {}).get("activation", {}).get("start") or 0) + 1
    hoep_et = int(activated_programs.get("hoep", {}).get("activation", {}).get("end") or 0) + 1
    ga_status = int(activated_programs.get("ga", {}).get("status", False))
    dr_status = int(activated_programs.get("dr", {}).get("status", False))
    hoep_status = int(activated_programs.get("hoep", {}).get("status", False))

    ga_activation, dr_activation, hoep_activation = np.zeros((3, 24), dtype="int64")
    ga_activation[ga_st - 1 : ga_et] = 1
    dr_activation[dr_st - 1 : dr_et] = 1
    hoep_activation[hoep_st - 1 : hoep_et] = 1

    activation_mode = np.zeros(24, dtype="int32")

    if hoep_status:
        activation_mode[hoep_activation == 1] = 1
    if dr_status:
        activation_mode[dr_activation == 1] = 1
    if ga_status:
        activation_mode[ga_activation == 1] = 1

    return activation_mode.tolist()


def check_for_update_load(new_data: dict, old_data: dict):
    """
    Check if load data has changed

    Parameters
    ----------
    new_data: dict
    old_data: dict

    Returns
    -------
    status: bool
    """

    new = new_data["load"][tznow(TIMEZONE).hour + 1 :]
    old = old_data["load"][tznow(TIMEZONE).hour + 1 :]

    if new != old:
        return True
    return False


def check_activation_program_status(program_name: str, program_data: dict) -> None:
    """Checking the update status of a program to send the alarm

    If we have already taken the status of a program, we compare the program cache data
     with the new received data.

    The mode in which the alarm is set:
    1- Have a change in the status of the program (true -> false or false -> true)
    2- If there is no change in the program status and if the program status is true,
       the changes in the start and end times of the program will be checked.

    """
    programs = Program.filter_by(is_global=True, name=program_name).all()

    if redis.exists(program_name):
        program_cache_data = json.loads(redis.get(program_name))
        delivery_date = parser.parse(program_cache_data.get("delivery_date"))
        changes = get_dict_diff(program_data, program_cache_data)
        redis.set(program_name, json.dumps(program_data))

        if tznow(TIMEZONE).date() > delivery_date.date():
            for program in programs:
                update_activation_db(program.id, program_data)

            return
            # calculate_pcs_battery_consumption()

        if check_status_changes(changes) or (
            not check_status_changes(changes) and check_activation_times_changes(changes) and program_data.get("status")
        ):
            for program in programs:
                alarm_status = json.loads(redis.get("need-update")) if redis.exists("need-update") else {}
                alarm_status[f"{program.battery_id}"] = 1
                redis.set("need-update", json.dumps(alarm_status))
                update_activation_db(program.id, program_data)

                Alarm.create(
                    commit=True,
                    date=tznow(TIMEZONE).date(),
                    program_id=program.id,
                    content=changes,
                    receive_time=tznow(TIMEZONE),
                    action=Action.idle,
                    battery_id=program.battery_id,
                )

        return

    redis.set(program_name, json.dumps(program_data))
    for program in programs:
        Activation.create(
            commit=True,
            date=tznow(TIMEZONE).date(),
            program_id=program.id,
            is_manual=False,
            status=program_data.get("status"),
            start=program_data.get("activation", {}).get("start"),
            end=program_data.get("activation", {}).get("end"),
        )
    # calculate_pcs_battery_consumption()


def check_status_changes(changes: dict) -> bool:
    """
    Check the status of the program.

    Returns
    -------
    bool : True if the program status has changed.
    """

    return True if "status" in changes.keys() else False


def check_activation_times_changes(changes: dict) -> bool:
    """
    Check the activation times of the program.

    Returns
    -------
    bool : True if the program activation times have changed.
    """

    return True if ("start" in changes.keys()) or ("end" in changes.keys()) else False


def update_activation_db(program_id: int, program_data: dict) -> None:
    activation = Activation.get_or_create(date=tznow(TIMEZONE).date(), program_id=program_id, is_manual=False)
    activation.update(
        commit=True,
        status=program_data.get("status"),
        start=program_data.get("activation", {}).get("start"),
        end=program_data.get("activation", {}).get("end"),
    )
