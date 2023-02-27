import json
import logging

import requests
from dateutil import parser

from backend.configs import TIMEZONE
from backend.utils import tznow

from .client import CoreAPIClient
from .exceptions import UnauthorizedError
from .logger import logger
from .utils import customize_component_data, validate_response


class CoreAPI:
    """Class to getting data from core API."""

    def __init__(self, username: str, password: str, debug: bool = False):
        self.client = CoreAPIClient(username=username, password=password, debug=debug)
        try:
            self.client.do_authentication_request()
        except Exception as exc:
            logger.error("Error during authentication: %s", exc)

        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)

    def _fetch(self, uri: str, **kwargs):
        url = f"{self.client.CORE_BASE_URL}{uri}"
        logger.info("Fetching '%s'", url)

        return validate_response(self.client.session.get(url, **kwargs))

    def _post(self, uri: str, **kwargs):
        url = f"{self.client.CORE_BASE_URL}{uri}"
        logger.info("Posting to '%s'", url)

        return validate_response(self.client.session.post(url, **kwargs))

    def get_component_data(self, start: str, end: str, component_id: int) -> dict:
        url = "/core/algorithm/series"

        payload = json.dumps(
            {
                "algorithm_name": "Baseline",
                "interval": "1h",
                "component_id": component_id,
                "start": start,
                "end": end,
                "fill_missing": True,
            }
        )

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": self.client.token,
        }

        try:
            response = self._post(url, headers=headers, data=payload)

        except UnauthorizedError:
            self.client.fix_token()
            response = self._post(url, headers=headers, data=payload)

        return customize_component_data(response)

    def _get_ga_activation_hours(self) -> dict:
        url = "/ds/window?location=ca-on"

        payload = json.dumps({"hours": 2})

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": self.client.token,
        }

        try:
            response = self._fetch(url, headers=headers, data=payload)

        except UnauthorizedError:
            self.client.fix_token()
            response = self._post(url, headers=headers, data=payload)

        activation_hours = response.get("result", {}).get("window", [])[-1]

        return {
            "start": int(activation_hours.get("start")),
            "end": int(activation_hours.get("end")) - 1,
        }

    def _get_ga_status(self):
        url = "/ds/estimation?location=ca-on"

        headers = {
            "Content-Type": "application/json",
            "Authorization": self.client.token,
        }

        try:
            response = self._fetch(url, headers=headers)

        except UnauthorizedError:
            self.client.fix_token()
            response = self._fetch(url, headers=headers)

        current_est = response.get("result", {}).get("peak_probability")

        return True if (current_est and int(current_est) >= 85) else False

    def get_ga_data(self):
        """
        Get the data of the Global Adjustment program.

        Returns
        -------
        dict : The data of the GA program (status and activation hours).
        """
        return {
            "delivery_date": tznow(TIMEZONE).date().strftime("%Y-%m-%d"),
            "status": self._get_ga_status(),
            "activation": self._get_ga_activation_hours(),
        }

    def _get_dr_status(self, zone: str, time: str) -> dict:
        """Get the status of the demand response program.

        Parameters
        ----------
        zone
        time

        Returns
        -------
        dict: DR program data such as:
            - start and end time
            - created_at
            - delivery_date
            - status and zone.
        """
        url = "https://api.edgecom.io/core/algorithm/json/global"
        payload = json.dumps({"algorithm_name": "DRStatus", "key": zone, "time": time})
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=payload, timeout=5)

        if response.status_code != 200:
            raise Exception(response.text)

        return json.loads(response.text)

    def _customize_dr_data(self, response):
        """Customize demand response data

        Parameters
        ----------
        response : requests.Response
            response of getting dr data in dictionary format

        Returns
        -------
        dict: DR program data such as:
            - activation times (start and end time)
            - delivery_date
            - status and zone.
        """
        data = response.get("result", {})
        customized_data = dict()

        if data.get("status", "") == "Demand Response Curtailment Required":
            customized_data["status"] = True
        else:
            customized_data["status"] = False

        if data.get("activation", {}).get("start") != "null" and data.get("activation", {}).get("end") != "null":
            customized_data["activation"] = {}
            customized_data["activation"]["start"] = int(data.get("activation", {}).get("start").split(":")[0])
            customized_data["activation"]["end"] = int(data.get("activation", {}).get("end").split(":")[0])

        customized_data["delivery_date"] = parser.parse(data.get("delivery_date")).date().strftime("%Y-%m-%d")

        return customized_data

    def get_dr_data(self, zone: str, time: str) -> dict:
        """
        Get the data of the demand response program.

        Parameters
        ----------
        zone: The requested zone that you want to get information
        time: requested date in "%Y-%m-%dT%H:%M:%S" format

        Returns
        -------
        dict: DR program data
        """
        data = self._get_dr_status(zone, time)
        return self._customize_dr_data(data)

    def get_last_update(self, name: str, component_id: int):
        url = f"/core/algorithm/{name}/{component_id}/last-update"

        headers = {
            "Accept": "application/json",
            "Authorization": self.client.token,
        }

        try:
            response = self._fetch(url, headers=headers)

        except UnauthorizedError:
            self.client.fix_token()
            response = self._fetch(url, headers=headers)

        return response
