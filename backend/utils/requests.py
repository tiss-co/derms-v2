from typing import Any, Mapping, Optional

from werkzeug.wrappers import Request


def get_value_from_request_by_key(request: Request, key: str, default: Any = None) -> Any:
    """
    Get value from request by the key. If the key is not found, returns the default
    value. args, body, and headers are searched in order.

    Parameters
    ----------
    request : Request
        The request.
    key : str
        The key to search for.
    default : Any
        The default value to return if the key is not found.

    Returns
    -------
    Any
        The value.
    """

    args = request.args
    _body = request.get_json(force=True, silent=True)
    body: Mapping = {} if _body is None else _body
    headers = request.headers

    if key in args:
        return args[key]
    elif key in body:
        return body[key]
    elif key in headers:
        return headers[key]
    else:
        return default


def get_token_from_request(request: Request) -> Optional[str]:
    """
    Get token from request.

    Parameters
    ----------
    request : Request
        The request.

    Returns
    -------
    Optional[str]
        The token.
    """

    if "token" in request.args:
        return request.args["token"]
    elif "Authorization" in request.headers:
        return request.headers["Authorization"].replace("Bearer ", "", 1)
    else:
        return None
