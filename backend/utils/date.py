import datetime
from typing import Optional

from dateutil import tz


def utcnow():
    """Returns a current timezone-aware datetime.datetime in UTC"""

    return datetime.datetime.now(datetime.timezone.utc)


def tznow(tzinfo: Optional[str] = None) -> datetime.datetime:
    """
    Returns a current timezone-aware datetime.datetime in the given timezone.

    Parameters
    ----------
    tzinfo : Optional[str]
        Timezone to use. If None, UTC is used. Pass `""` to use localtime.

    Returns
    -------
    datetime.datetime
        A current timezone-aware datetime.

    Raises
    ------
    ValueError
        If the given timezone is not recognized. All `dateutil.zoneinfo` timezones are
        currenty supported.
    """

    if tzinfo is None:
        return utcnow()

    tzfile = tz.gettz(tzinfo)
    if tzfile is None:
        raise ValueError(f"Timezone `{tzinfo}` is not recognized.")

    return datetime.datetime.now(tz=tzfile)
