from flask import Blueprint

root: Blueprint = Blueprint(name="root", import_name=__name__, url_prefix="/derms/")
alarm: Blueprint = Blueprint(name="alarm", import_name=__name__, url_prefix="/derms/alarm/")
battery: Blueprint = Blueprint(name="battery", import_name=__name__, url_prefix="/derms/battery/")
activation: Blueprint = Blueprint(name="activation", import_name=__name__, url_prefix="/derms/activation/")
program: Blueprint = Blueprint(name="program", import_name=__name__, url_prefix="/derms/program/")


from backend.api.alarm import alarm_accept, get_alarm_content, get_alarm_status
from backend.api.battery import get_battery_details, get_battery_load, get_pcs_battery_consumption, get_voltage_current
from backend.api.health.views import health, healthcheck, ping
from backend.api.activation import get_activated_programs, get_total_activation_hours, set_program_activation_status
from backend.api.program.views import create_program