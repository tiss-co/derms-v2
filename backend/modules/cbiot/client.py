import json
import logging

import requests

from .cookie_repository import CookieRepository
from .logger import logger
from .utils import validate_response


class Client(object):
    """Class to act as a client for the CBIOT API."""

    CBIOT_BASE_URL: str = "https://api-bms.edgecom.io"
    LOGIN_BASE_URL: str = f"{CBIOT_BASE_URL}/login"

    REQUEST_HEADERS = {"Content-Type": "application/json"}

    def __init__(self, username: str, password: str, debug: bool = False) -> None:
        self.username = username
        self.password = password
        self.debug = debug
        self.session = requests.session()
        self.session.headers.update(Client.REQUEST_HEADERS)
        self.cookie_name = f"{username}_cookie"

        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)

    def _request_session_token(self):
        """
        Authenticate with the CBIOT API.

        Returns:
        -------
        str: a new session Bearer token
        """

        logger.info("Trying to login to CBIOT...")

        payload = json.dumps({"username": self.username, "password": self.password})

        response = requests.post(Client.LOGIN_BASE_URL, data=payload)
        data = validate_response(response)

        logger.info("You are successfully logged in.")

        token = data.get("token")
        bearer_token = "Bearer " + token

        return bearer_token

    def _set_authorization_header(self, token):
        """
        Set authorization header for the session.
        """
        self.session.headers["Authorization"] = token

    @property
    def token(self):
        """
        Get the bearer token for the session.
        """
        return self.session.headers["Authorization"]

    def do_authentication_request(self):
        """
        Authenticate with the CBIOT API.
        """

        try:
            token = CookieRepository.get(self.cookie_name)
            self._set_authorization_header(token)

        except FileNotFoundError:
            pass

        self._set_authorization_header(self._request_session_token())
        CookieRepository.save(self.token, self.cookie_name)

    def fix_token(self):
        self._set_authorization_header(self._request_session_token())
        CookieRepository.save(self.token, self.cookie_name)
