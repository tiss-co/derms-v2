import json
import random
import time
from datetime import datetime

import pandas as pd
import requests

from .exceptions import BadRequest, HTTPError, UnauthorizedError


def default_evade():
    time.sleep(random.randint(2, 5))  # sleep a random duration to try and evade suspension


def validate_response(response: requests.Response):
    """validate response status code and raise exception if not in (200, 201, 204, 302)."""
    status = response.status_code

    try:
        message = response.json().get("message", response.content)
    except json.JSONDecodeError:
        message = ""

    if status in (500, 401, 403, 404):
        raise UnauthorizedError(message)

    elif status == 400:
        raise BadRequest(message)

    elif status in (200, 201, 204, 302):
        try:
            response = response.json()
        except json.JSONDecodeError:
            response = {}
        return response

    raise HTTPError(
        f"{response.status_code}",
        f"{str(response.reason).upper().replace(' ', '_')}: {response.url}",
    )


def customize_component_data(comp_res: dict) -> list:
    comp_data = comp_res.get("result")[0]
    comp_df = pd.DataFrame(comp_data.get("values"))

    if comp_df["value"].isnull().values.any():
        return []

    else:
        comp_df["value"] = comp_df["value"] * 0.50
        comp_df["time"] = pd.to_datetime(comp_df["time"])
        comp_df["datetime"] = pd.to_timedelta(comp_df.time.dt.strftime("%H:%M:%S")) + pd.to_datetime(
            comp_data.get("date")
        )
        comp_df = comp_df.astype({"datetime": str, "value": int})
        return comp_df[["datetime", "value"]].to_dict(orient="records")
