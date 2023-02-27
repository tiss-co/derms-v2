from backend.logger import logger
from backend.models import User
from backend.utils import get_token_from_request
from flask import current_app
from werkzeug.wrappers import Request


def check_request_credentials(request: Request, require_admin_privilege=True) -> bool:
    """
    Check if the request has the credential.

    Parameters
    ----------
    request : Request
        The request.
    require_admin_privilege : bool
        Whether to require admin privilege. Default is `True`.

    Returns
    -------
    bool
        True if the request has the credential, otherwise False.
    """

    if current_app.config.get("DEBUG") is True:
        logger.warning("DEBUG is True, skipping authentication...")
        return True

    token = get_token_from_request(request)
    if not token:
        return False

    user = User.get_by(token, require_admin_privilege)
    if user and user.is_authenticated() is True:
        return True

    return False
