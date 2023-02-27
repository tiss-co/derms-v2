from requests.exceptions import HTTPError


class UnauthorizedError(Exception):
    """401 Unauthorized"""
    pass


class ForbiddenError(Exception):
    """403 Forbidden"""
    pass


class NotFoundError(Exception):
    """404 Not Found"""
    pass


class SessionExpiredError(Exception):
    """419 Session Expired"""
    pass


class InternalServerError(Exception):
    """500 Internal Server Error"""
    pass
