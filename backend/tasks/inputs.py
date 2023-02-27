import json
from datetime import datetime, timedelta
from random import randint
from time import sleep

from dateutil import parser

from backend.configs import DEMAND_RESPONSE_ZONE, TIMEZONE
from backend.database import session
from backend.extensions import redis, scheduler
from backend.extensions.core_api import core_api
from backend.logger import logger
from backend.models import Battery, Load
from backend.utils import tznow

from . import teardown_taskcontext
from .utils import (
    calculate_pcs_battery_consumption,
    check_activation_program_status,
    check_for_update_load,
    daily_activity_hours,
)


@teardown_taskcontext
def get_loads() -> None:
    logger.info("Trying to get loads data...")

    with scheduler.app.app_context():
        try:
            start_date = datetime.combine(
                tznow(TIMEZONE).date(), datetime.min.time()
            ).strftime("%Y-%m-%dT%H:%M:%S")
            end_date = datetime.combine(
                (tznow(TIMEZONE) + timedelta(days=1)).date(), datetime.min.time()
            ).strftime("%Y-%m-%dT%H:%M:%S")

            comp_list = [
                row.component_id
                for row in session.query(Battery.component_id).distinct()
            ]

            if redis.exists("LOAD"):
                load_cache_data = json.loads(redis.get("LOAD"))

                for comp_id in comp_list:
                    try:
                        cached_last_update = load_cache_data.get(str(comp_id))
                        comp_last_update = core_api.get_last_update(
                            name="Baseline", component_id=comp_id
                        )
                        new_last_update = comp_last_update.get("result", {}).get(
                            "lastUpdate"
                        )

                        if parser.parse(new_last_update) > parser.parse(
                            cached_last_update
                        ):
                            update_load_cache(comp_id, new_last_update)
                            comp_values = core_api.get_component_data(
                                start=start_date, end=end_date, component_id=comp_id
                            )

                            update_load_table(comp_id, comp_values)

                    except Exception as exc:
                        continue

            else:
                for comp_id in comp_list:
                    comp_values = core_api.get_component_data(
                        start=start_date, end=end_date, component_id=comp_id
                    )

                    try:
                        comp_last_update = core_api.get_last_update(
                            name="Baseline", component_id=comp_id
                        )
                        lu = comp_last_update.get("result", {}).get("lastUpdate")
                        parser.parse(lu)
                        update_load_cache(comp_id, lu)
                        update_load_table(comp_id, comp_values)

                    except:
                        continue

            sleep(randint(1, 5))  # noexec

        except Exception as exc:
            logger.error("A problem in gathering load data: %s", exc)


def update_load_table(comp_id: int, comp_data: list):
    for item in comp_data:
        item_date = parser.parse(item.get("datetime"))
        item_value = float(item.get("value"))
        load = Load.get_or_create(datetime=item_date, component_id=comp_id)
        load.update(commit=True, value=item_value)


def update_load_cache(comp_id: int, last_update: str):
    if redis.exists("LOAD"):
        cached_last_update = json.loads(redis.get("LOAD"))
        cached_last_update[comp_id] = last_update
        redis.set("LOAD", json.dumps(cached_last_update))

    else:
        redis.set("LOAD", json.dumps({str(comp_id): last_update}))


@teardown_taskcontext
def get_ga_status() -> None:

    with scheduler.app.app_context():
        try:

            logger.info("Trying to get Global Adjustment data automatically...")
            ga_data = core_api.get_ga_data()

            check_activation_program_status("GA", ga_data)

            sleep(randint(1, 5))  # noexec

        except Exception as exc:
            logger.error("A problem in gathering ga data: %s", exc)


@teardown_taskcontext
def get_dr_status() -> None:

    with scheduler.app.app_context():
        try:

            logger.info("Trying to get Demand Response data automatically...")

            today = (
                tznow(TIMEZONE).replace(hour=0, minute=0, second=0, microsecond=0)
                - timedelta(days=2)
            ).strftime("%Y-%m-%dT%H:%M:%S")
            dr_data = core_api.get_dr_data(zone=DEMAND_RESPONSE_ZONE, time=today)

            check_activation_program_status("DR", dr_data)

            sleep(randint(1, 5))  # noexec

        except Exception as exc:
            logger.error("A problem in gathering DR data: %s", exc)
