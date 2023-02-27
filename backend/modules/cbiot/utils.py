import json
import random
import time

import requests

from .exceptions import HTTPError, UnauthorizedError


def default_evade():
    time.sleep(
        random.randint(2, 5)
    )  # sleep a random duration to try and evade suspension


def validate_response(response: requests.Response):
    """validate response status code and raise exception if not in (200, 201, 204, 302)."""
    status = response.status_code

    try:
        message = response.json().get("message", response.text)
    except json.JSONDecodeError:
        message = ""

    if status in (500, 401, 403, 404):
        raise UnauthorizedError(message)

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
