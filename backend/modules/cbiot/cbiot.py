import json
import logging

from .client import Client
from .exceptions import UnauthorizedError
from .logger import logger
from .settings import *
from .utils import validate_response


class CBIOT:
    def __init__(self, username: str, password: str, debug: bool = False):
        self.client = Client(username=username, password=password, debug=debug)
        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)

    def _fetch(self, uri: str, **kwargs):
        url = f"{self.client.CBIOT_BASE_URL}{uri}"
        logger.info("Fetching '%s'", url)

        return validate_response(self.client.session.get(url, **kwargs))

    def _post(self, uri: str, **kwargs):
        url = f"{self.client.CBIOT_BASE_URL}{uri}"
        logger.info("Posting to '%s'", url)

        return validate_response(self.client.session.post(url, **kwargs))

    def _put(self, uri: str, **kwargs):
        url = f"{self.client.CBIOT_BASE_URL}{uri}"
        logger.info("Putting to '%s'", url)

        return validate_response(self.client.session.put(url, **kwargs))

    def get_modbus_tag_data(self, tag: str, period: str):
        uri = f"/tag/{tag}/data?period={period}"
        try:
            response = self._fetch(uri=uri)
        except UnauthorizedError:
            self.client.fix_token()
            response = self._fetch(uri=uri)

        return response

    def get_modbus_tag_data_range(self, tag: str, start: str, end: str):
        uri = f"/tag/{tag}/data/range?date_start={start}&date_end={end}"
        try:
            response = self._fetch(uri=uri)
        except UnauthorizedError:
            self.client.fix_token()
            response = self._fetch(uri=uri)
        return response

    def get_modbus_tag_data_last(self, tag: str, period: str):
        uri = f"/tag/{tag}/data/last?period={period}"
        try:
            response = self._fetch(uri=uri)
        except UnauthorizedError:
            self.client.fix_token()
            response = self._fetch(uri=uri)
        return response

    def send_modbus_command(self, tag, params):
        payload = json.dumps({"params": int(f"{params}")})
        uri = f"/protocol/tag/{tag}/command"

        try:
            self._put(uri=uri, data=payload)
        except UnauthorizedError:
            self.client.fix_token()
            self._put(uri=uri, data=payload)

    # get data from CBIOT (battery)
    def get_state_of_charge(self):
        data = self.get_modbus_tag_data_last(tag=STATE_OF_CHARGE_TAG, period=CBIOT_TIME)
        return float(data.get("value")) if data and data.get("value") != "" else None

    def get_life_cycle(self):
        data = self.get_modbus_tag_data_last(tag=LIFE_CYCLE_TAG, period=CBIOT_TIME)
        return float(data.get("value")) if data and data.get("value") != "" else None

    def get_state_of_health(self):
        data = self.get_modbus_tag_data_last(tag=STATE_OF_HEALTH_TAG, period=CBIOT_TIME)
        return float(data.get("value")) if data and data.get("value") != "" else None

    def get_bdc_mode(self):
        data = self.get_modbus_tag_data_last(tag=BDC_MODE_TAG, period=CBIOT_TIME)
        return float(data.get("value")) if data and data.get("value") != "" else None

    def get_power_limit(self):
        data = self.get_modbus_tag_data_last(tag=POWER_LIMIT_TAG, period=CBIOT_TIME)
        return float(data.get("value")) if data and data.get("value") != "" else None

    def get_voltage(self):
        data = self.get_modbus_tag_data_last(tag=VOLTAGE_TAG, period=CBIOT_TIME)
        return float(data.get("value")) if data and data.get("value") != "" else None

    def get_current(self):
        data = self.get_modbus_tag_data_last(tag=CURRENT_TAG, period=CBIOT_TIME)
        return float(data.get("value")) if data and data.get("value") != "" else None

    def get_grid_frequency(self):
        data = self.get_modbus_tag_data_last(tag=GRID_FREQUENCY_TAG, period=CBIOT_TIME)
        return float(data.get("value")) if data and data.get("value") != "" else None

    def get_average_grid_current(self):
        data = self.get_modbus_tag_data_last(tag=AVERAGE_GRID_CURRENT_TAG, period=CBIOT_TIME)
        return float(data.get("value")) if data and data.get("value") != "" else None

    def get_grid_reactive_power(self):
        data = self.get_modbus_tag_data_last(tag=GRID_REACTIVE_POWER_TAG, period=CBIOT_TIME)
        return float(data.get("value")) if data and data.get("value") != "" else None

    def get_grid_power_factor(self):
        data = self.get_modbus_tag_data_last(tag=GRID_POWER_FACTOR_TAG, period=CBIOT_TIME)
        return float(data.get("value")) if data and data.get("value") != "" else None

    def get_ambient_temperature(self):
        data = self.get_modbus_tag_data_last(tag=AMBIENT_TEMPERATURE_TAG, period=CBIOT_TIME)
        return float(data.get("value")) if data and data.get("value") != "" else None

    # send data to CBIOT (battery)
    def set_bdc_mode(self, value: int):
        self.send_modbus_command(tag=SET_BDC_MODE_TAG, params=value)

    def set_power_limit(self, value: int):
        self.send_modbus_command(tag=SET_POWER_LIMIT_TAG, params=value)
