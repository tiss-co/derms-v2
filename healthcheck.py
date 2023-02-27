import logging
import sys
from urllib.request import urlopen

from backend.configs import FLASK_FORCE_HTTPS, FLASK_HOST, FLASK_PORT

HEALTHCHECK_URL: str = f"{'https' if FLASK_FORCE_HTTPS is True else 'http'}://{FLASK_HOST}:{FLASK_PORT}/healthcheck"

logger: logging.Logger = logging.getLogger(__name__)


def get_status():
    """
    A simple healthcheck endpoint to check if the server is responding.

    Raises
    ------
    ConnectionError
        - if the server is not responding.
    """

    try:
        if (
            urlopen(
                url=HEALTHCHECK_URL,
                timeout=15,
            ).getcode()
            == 200
        ):
            logger.info("HEALTHCHECK - '%s' 200", HEALTHCHECK_URL)
            sys.exit(0)

        else:
            raise ConnectionError(
                f"HEALTHCHECK - {HEALTHCHECK_URL!r} is not available ..."
            )

    except Exception:
        logger.error("HEALTHCHECK - '%s' is not available ...", HEALTHCHECK_URL)
        sys.exit(1)
