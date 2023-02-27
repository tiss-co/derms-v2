import re
import unicodedata

from backend.logger import logger
from flask import current_app, jsonify
from flask_sqlalchemy.model import camel_to_snake_case


def log_expection(exc: Exception, exc_info: bool = True) -> None:
    """Logs the exception to the logger."""

    if current_app.config.get("DEBUG") is True:
        logger.error(
            exc,
            exc_info,
        )


def send_error_response(error_message, status_code):
    """Sends an error response to the client."""

    return (
        jsonify({"result": error_message}),
        status_code,
    )


def slugify(string: str) -> str:
    """
    Converts the input string to the equivalent slugify form.

    Parameters
    ----------
    string : [str]
        Input string.

    Examples
    --------
    >>> slugify("Hello, World!")
    "hello-world"

    Returns
    -------
    [str]
        Slugify form of the string.
    """

    string = re.sub(r"[^\w\s-]", "", unicodedata.normalize("NFKD", str(string).strip()))

    return re.sub(r"[-\s]+", "-", string).lower()


def title_case(string: str) -> str:
    """
    Converts the input string to the equivalent title case form.

    Parameters
    ----------
    string : [str]
        Input string.

    Examples
    --------
    >>> title_case("hello, world!")
    "Hello, World!"

    Returns
    -------
    [str]
        Title case form of the string.
    """

    return camel_to_snake_case(string).replace("_", " ").title()


def pluralize(name: str):
    """
    Converts the input string to the equivalent pluralize form.

    Parameters
    ----------
    string : [str]
        Input string.

    Examples
    --------
    >>> pluralize("Book")
    "Books"

    Returns
    -------
    [str]
        Pluralize form of the string.
    """

    if name.endswith("y"):
        # right replace 'y' with 'ies'
        return "ies".join(name.rsplit("y", 1))
    elif name.endswith("s"):
        return f"{name}es"

    return f"{name}s"
