from flask import jsonify
from werkzeug.wrappers import Response

from backend.extensions.blueprints import root


@root.route("/health", methods=["GET"])
def health() -> Response:
    """
    used to check the API health.
    """

    return jsonify(result="Ok!")


@root.route("/healthcheck", methods=["GET"])
def healthcheck() -> Response:
    """
    used to check the API health.
    """

    return jsonify(result="Ok!")


@root.route("/ping", methods=["GET"])
def ping() -> Response:
    """
    used to check the API health.
    """

    return jsonify(result="Ok!")
