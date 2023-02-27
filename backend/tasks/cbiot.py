from datetime import datetime, time

from backend.configs import TIMEZONE
from backend.database import session
from backend.extensions import scheduler
from backend.extensions.cbiot import cbiot
from backend.logger import logger
from backend.models import BatteryDetails, PowerQuality, Result
from backend.modules.derms import settings
from backend.utils import tznow


def calculate_ambient_temperature(temperature):
    if temperature > 56:
        cal_temp = temperature - 55
    else:
        cal_temp = -temperature
    return cal_temp


def calculate_power_factor(pf):
    if pf > 100:
        cal_pf = pf - 100
    else:
        cal_pf = -pf
    return cal_pf / 100


def handle_soc_min():
    """
    This function is used to handle SOC min according to the battery settings.

    Returns
    -------
    None
    """
    logger.debug("Try to handle SOC min...")

    try:
        soc = cbiot.get_state_of_charge()
        bdc = cbiot.get_bdc_mode()
        pl = cbiot.get_power_limit()

        if any(v is None for v in [soc, bdc, pl]):
            logger.info("SOC min can not handled, because some data is missing.")

        else:
            if soc <= 12 and bdc == 0 and pl > 0:
                cbiot.set_bdc_mode(13)

    except Exception as exc:
        logger.error("Problem in handle soc: %s", str(exc))


def power_command():
    """
    Try sending a charge/discharge command to CBiOT based on the calculated results every hour.

    Returns
    -------
    None
    """
    logger.debug("Try to send command to cbiot service...")

    with scheduler.app.app_context():
        result = (
            session.query(Result)
            .filter(Result.datetime == datetime.combine(tznow(TIMEZONE).date(), time(tznow(TIMEZONE).hour, 0)))
            .first()
        )

        try:
            if result:
                if result.charging_status == 0:
                    cbiot.set_bdc_mode(13)
                elif result.charging_status == 1:
                    cbiot.set_bdc_mode(0)
                    cbiot.set_power_limit(-100)
                elif result.charging_status == -1:
                    cbiot.set_bdc_mode(0)
                    cbiot.set_power_limit(100)

                logger.info("Command was sent successfully.")
            else:
                return

        except Exception as e:
            logger.error(e.__str__())


def battery_details():
    """
    Try to get battery details from CBiOT.

    Returns
    -------
    None
    """
    logger.debug("Try to get battery details from cbiot service...")

    with scheduler.app.app_context():

        try:

            soc = cbiot.get_state_of_charge()
            life_cycle = cbiot.get_life_cycle()
            soh = cbiot.get_state_of_health()
            frequency = cbiot.get_grid_frequency()
            average_grid_current = cbiot.get_average_grid_current()
            reactive_power = cbiot.get_grid_reactive_power()
            ambient_temperature = cbiot.get_ambient_temperature()
            power_factor = cbiot.get_grid_power_factor()
            power_limit = cbiot.get_power_limit()
            bdc = cbiot.get_bdc_mode()
            battery_status = None

            if bdc:
                if int(bdc) == 13:
                    battery_status = "idle"

                elif int(bdc) == 0:
                    p_limit = int(power_limit)
                    if p_limit >= 0:
                        battery_status = "discharge"
                    if p_limit < 0:
                        battery_status = "charge"

            current_details = BatteryDetails.get_or_create(
                datetime=datetime.combine(tznow(TIMEZONE).date(), time(tznow(TIMEZONE).hour, 0))
            )

            current_details.update(
                commit=True,
                current_status=battery_status,
                p_max=settings.p_max,
                p_max_charge=settings.charge_max,
                capacity=settings.BATTERY_CAPACITY,
                available_energy=(round(soc) * settings.BATTERY_CAPACITY / 100) if soc else 600,
                state_of_charge=soc if soc else 48,
                remaining_life_cycle=settings.TOTAL_LIFE_CYCLE - life_cycle if life_cycle else 7000,
                state_of_health=soh / 10 if soh else 95,
                grid_frequency=frequency / 100 if frequency else 60,
                average_grid_current=average_grid_current / 10 if average_grid_current else 300,
                reactive_power=reactive_power / 10 if reactive_power else 50,
                ambient_temperature=calculate_ambient_temperature(ambient_temperature) if ambient_temperature else 25,
                power_factor=calculate_power_factor(power_factor) if power_factor else 0.98,
            )

        except Exception as exc:
            logger.error("failed to fetch cbiot data: %s", str(exc))


# @scheduler.task("cron", id="VOLTAGE_CURRENT", minute="*/15")
def voltage_current():
    with scheduler.app.app_context():
        voltage, current = None, None
        current_facility, current_utility, current_battery = None, None, None

        try:
            voltage = cbiot.get_voltage()
            current = cbiot.get_current()

        except Exception as exc:
            logger.error("failed to fetch cbiot data: %s", str(exc))

        voltage = (voltage / 10) if voltage else 480
        current = (current / 10) if current else 300

        voltage_utility, voltage_facility, voltage_battery = voltage, voltage, voltage

        now_results = Result.get_or_create(
            datetime=datetime.combine(tznow(TIMEZONE).date(), time(tznow(TIMEZONE).hour, 0))
        )

        charging_status = now_results.charging_status if now_results else 0
        power = (int(now_results.power) * 1000) if now_results else 250000

        if charging_status == 0:
            current_facility = current
            current_utility = current
            current_battery = 0

        elif charging_status == 1:
            current_battery = float(power / (1.7 * voltage_utility * 0.9))
            current_utility = current
            current_facility = current_utility - current_battery

        elif charging_status == -1:
            current_battery = float(power / (1.7 * voltage_utility * 0.9))
            current_utility = 0
            current_facility = current_battery

        now_voltage_current = PowerQuality.get_or_create(
            datetime=datetime.combine(tznow(TIMEZONE).date(), time(tznow(TIMEZONE).hour, 0))
        )

        now_voltage_current.update(
            commit=True,
            voltage_utility=voltage_utility,
            voltage_battery=voltage_battery,
            voltage_facility=voltage_facility,
            current_utility=current_utility,
            current_battery=current_battery,
            current_facility=current_facility,
        )

        logger.debug("current voltage updated successfully")
