import json
import logging

import requests

from .cookie_repository import CookieRepository
from .logger import logger
from .utils import validate_response


class CoreAPIClient(object):
    """Class to act as a client for the Edgecom core API."""

    CORE_BASE_URL: str = "https://api.edgecom.io"
    LOGIN_BASE_URL: str = f"{CORE_BASE_URL}/umg/login"

    def __init__(self, username: str, password: str, debug: bool = False) -> None:
        self._cookies = None
        self.username = username
        self.password = password
        self.cookie_name = f"{username}_cookie"
        self.debug = debug
        self.session = requests.session()

        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)

    def _request_session_token(self):
        """
        Request a session token from the Edgecom Core API.
        Returns
        -------
        str: Session token.
        """

        logger.info("Trying to login to core api...")

        headers = {"accept": "application/json", "Content-Type": "application/json"}

        payload = json.dumps({"username": self.username, "password": self.password})

        response = requests.post(self.LOGIN_BASE_URL, headers=headers, data=payload)
        data = validate_response(response)

        logger.info("You are successfully logged in.")

        token = data.get("result", {}).get("token")
        bearer_token = "Bearer " + token

        return bearer_token

    def _set_authorization_header(self, token: str) -> None:
        """
        Set authorization header for the session.
        """
        self.session.headers["Authorization"] = token

    @property
    def token(self):
        """Get the bearer token for the session."""
        return self.session.headers["Authorization"]

    def do_authentication_request(self):
        """Authenticate with the Core API."""

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
