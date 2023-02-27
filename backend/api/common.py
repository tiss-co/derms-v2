import datetime

from backend.database import func
from backend.models import Load, ManualLoad
from backend.serializers import LoadSchema, ManualLoadSchema


def get_loads(date: datetime.date, comp_id: int) -> list:
    """Return the load object of the given date.

    manual_load is preferred over the load.

    Parameters
    ----------
    date : datetime.date
        The requested date to get load values.

    Returns
    -------
    list
        The load objects.
    """
    load_query = (
        Load.filter(func.date(Load.datetime) == date, Load.component_id == comp_id).order_by(Load.datetime)
    ).all()
    manual_load_query = (
        ManualLoad.filter(func.date(ManualLoad.datetime) == date, ManualLoad.component_id == comp_id).order_by(
            ManualLoad.datetime
        )
    ).all()

    load = list(map(dict, LoadSchema(many=True).dump(load_query)))
    manual_load = list(map(dict, ManualLoadSchema(many=True).dump(manual_load_query)))

    for load_item in load:
        for manual_load_item in manual_load:
            if load_item["datetime"] == manual_load_item["datetime"]:
                load_item["value"] = manual_load_item["value"]

    return load
