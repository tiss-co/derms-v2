from backend.app import create_app
from backend.extensions import scheduler
from backend.tasks.cbiot import battery_details, handle_soc_min, power_command, voltage_current
from backend.tasks.inputs import get_dr_status, get_ga_status, get_loads

app = create_app()

scheduler.add_job(id="loads", func=get_loads, trigger="interval", seconds=60)
scheduler.add_job(id="GA", func=get_ga_status, trigger="interval", seconds=61)
scheduler.add_job(id="DR", func=get_dr_status, trigger="interval", seconds=62)

scheduler.add_job(id="BATTERY_DETAILS", func=battery_details, trigger="cron", minute="*/5")
scheduler.add_job(id="HANDLE_SOC_MIN", func=handle_soc_min, trigger="cron", minute="*")
scheduler.add_job(id="POWER_COMMAND", func=power_command, trigger="cron", minute="*/5")
scheduler.add_job(id="VOLTAGE_CURRENT", func=voltage_current, trigger="cron", minute="*/15")

with app.app_context():
    scheduler.start()
