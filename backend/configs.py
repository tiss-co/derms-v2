import os
from functools import singledispatch
from typing import Any

# TODO: comment these lines on deployment.
try:
    from dotenv import load_dotenv

    load_dotenv()

except ImportError:
    pass


def get_environment_variable(cast: object, name: str, default: Any = None):
    """Get environment variable function.

    Get the environment variable or raise exception.

    Parameters
    ----------
    cast : object
        The type parameter to cast the environment variable to. use ```None``` to keep the type as is.
    name : str
        The environment variable name.
    default : Any, optional
        The default value to return if the environment variable does not exist, by default None

    Returns
    -------
    The casted environment variable.

    Raises
    ------
    EnvironmentError
        - if the environment variable does not exist.
    """

    def before_dispatch(cast: object, name: str, default: Any = None):
        """Get the environment variable before dispatch."""

        try:
            return process(cast, value=os.environ[name])
        except KeyError:
            if default is not None:
                return process(cast, value=default)
            else:
                raise EnvironmentError(
                    f"The environment variable {name} was missing, abort..."
                ) from KeyError

    @singledispatch
    def process(cast: object, value: Any) -> Any:
        """Process the environment variable."""

        return value

    @process.register(str)
    def strings(cast: object, value: Any) -> str:
        """Process the environment variable as a string."""

        return str(value)

    @process.register(int)
    def integers(cast: object, value: Any) -> int:
        """Process the environment variable as an integer."""

        return int(value)

    @process.register(float)
    def floats(cast: object, value: Any) -> float:
        """Process the environment variable as a float."""

        return float(value)

    @process.register(bool)
    def booleans(cast: object, value: Any) -> bool:
        """Process the environment variable as a boolean."""

        return str(value).lower() in (
            "true",
            "yes",
            "y",
            "1",
        )

    return before_dispatch(cast, name, default)


# flask app name constant
APP_NAME = get_environment_variable(
    cast=str(), name="COMPOSE_PROJECT_NAME", default="NotificationService"
)

# flask app directory constants
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

TEMPLATE_FOLDER = os.path.join(PROJECT_ROOT, "backend", "templates")
STATIC_FOLDER = os.path.join(PROJECT_ROOT, "www", "public")
MIGRATION_FOLDER = os.path.join(PROJECT_ROOT, "../migrations")

# urls must start with a leading slash
STATIC_URL_PATH = "/statics"  # serve asset files in STATIC_FOLDER at /statics/
UPLOAD_URL_PATH = (
    "/uploads"  # serve asset files in STATIC_FOLDER/STATIC_URL_PATH at /uploads/
)

# flask app host & port constants
FLASK_HOST = get_environment_variable(cast=str(), name="FLASK_HOST", default="0.0.0.0")
FLASK_PORT = get_environment_variable(cast=int(), name="FLASK_PORT", default=8088)
FLASK_FORCE_HTTPS = get_environment_variable(
    cast=bool(), name="FLASK_FORCE_HTTPS", default=False
)
ALLOWED_HOSTS = {"www.{FLASK_HOST}:{FLASK_PORT}", "{FLASK_HOST}:{FLASK_PORT}"}

CBIOT_USERNAME = get_environment_variable(cast=str(), name="CBIOT_USERNAME")
CBIOT_PASSWORD = get_environment_variable(cast=str(), name="CBIOT_PASSWORD")

UMG_CLIENT_HOST = get_environment_variable(cast=str(), name="UMG_CLIENT_HOST")
UMG_CLIENT_SSL = get_environment_variable(
    cast=bool(), name="UMG_CLIENT_SSL", default=True
)

CORE_API_USERNAME = get_environment_variable(cast=str(), name="CORE_API_USERNAME")
CORE_API_PASSWORD = get_environment_variable(cast=str(), name="CORE_API_PASSWORD")
COMPONENT_ID = get_environment_variable(cast=int(), name="COMPONENT_ID")
DEMAND_RESPONSE_ZONE = get_environment_variable(cast=str(), name="DEMAND_RESPONSE_ZONE")

TIMEZONE = get_environment_variable(cast=str, name="TIMEZONE")

DEBUG = get_environment_variable(cast=bool, name="DEBUG", default=False)

GLOBAL_PROGRAMS = ["GA", "DR", "HOEP"]
# ordered list of extensions to register before the bundles
# syntax is import.name.in.dot.module.notation:extension_instance_name
EXTENSIONS = [
    "backend.extensions:redis",
    "backend.extensions:db",
    "backend.extensions:migrate",  # must come after db
    "backend.extensions:scheduler",
    "backend.extensions:ma",  # must come after db
]


class FlaskBaseConfig(object):
    """Flask base config."""

    ###############################################################################
    # app                                                                         #
    ###############################################################################
    # flask app
    FLASK_ENV = get_environment_variable(
        cast=str(), name="FLASK_ENV", default="production"
    )
    FLASK_DEBUG = get_environment_variable(
        cast=bool(), name="FLASK_DEBUG", default=False
    )
    TESTING = get_environment_variable(cast=bool(), name="TESTING", default=False)

    ###############################################################################
    # redis                                                                       #
    ###############################################################################
    # redis cache database configurations
    REDIS_HOST = get_environment_variable(cast=str(), name="REDIS_HOST")
    REDIS_PORT = get_environment_variable(cast=int(), name="REDIS_PORT")
    REDIS_PASSWORD = get_environment_variable(
        cast=str(), name="REDIS_PASSWORD", default=""
    )
    REDIS_DB = get_environment_variable(cast=int(), name="REDIS_DB", default=0)

    ###############################################################################
    # database                                                                    #
    ###############################################################################
    # database configurations
    DATABASE_DIALECT = get_environment_variable(cast=str(), name="DATABASE_DIALECT")
    DATABASE_HOST = get_environment_variable(cast=str(), name="DATABASE_HOST")
    DATABASE_PORT = get_environment_variable(cast=int(), name="DATABASE_PORT")
    DATABASE_USERNAME = get_environment_variable(cast=str(), name="DATABASE_USERNAME")
    DATABASE_PASSWORD = get_environment_variable(cast=str(), name="DATABASE_PASSWORD")
    DATABASE_DB = get_environment_variable(cast=str(), name="DATABASE_DB")

    # flask-sqlalchemy
    SQLALCHEMY_DATABASE_URI = f"{DATABASE_DIALECT}://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = True if FLASK_DEBUG is True else False
    SQLALCHEMY_ECHO = True if FLASK_DEBUG is True else False
    # SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    ###############################################################################
    # security                                                                    #
    ###############################################################################
    # flask app
    SECRET_KEY = str(
        get_environment_variable(
            cast=str(), name="SECRET_KEY", default=os.urandom(32).hex()
        )
    )

    # flask-login
    SESSION_PROTECTION = get_environment_variable(
        cast=str(), name="SESSION_PROTECTION", default="strong"
    )
    REMEMBER_COOKIE_DURATION = get_environment_variable(
        cast=int(), name="REMEMBER_COOKIE_DURATION", default=3600
    )
    REMEMBER_COOKIE_HTTPONLY = get_environment_variable(
        cast=bool(), name="REMEMBER_COOKIE_HTTPONLY", default=True
    )
    REMEMBER_COOKIE_REFRESH_EACH_REQUEST = get_environment_variable(
        cast=bool(), name="REMEMBER_COOKIE_REFRESH_EACH_REQUEST", default=False
    )

    # werkzeug.security
    SECURITY_HASH_METHOD = get_environment_variable(
        cast=str(), name="SECURITY_HASH_METHOD", default="pbkdf2:sha256:1_000_000"
    )
    SECURITY_SALT_LENGHT = get_environment_variable(
        cast=int(), name="SECURITY_SALT_LENGHT", default=32
    )

    ###############################################################################
    # session/cookies                                                             #
    ###############################################################################
    # flask app
    SESSION_COOKIE_HTTPONLY = get_environment_variable(
        cast=bool(), name="SESSION_COOKIE_HTTPONLY", default=True
    )
    SESSION_COOKIE_SECURE = get_environment_variable(
        cast=bool(), name="SESSION_COOKIE_SECURE", default=True
    )
    SESSION_COOKIE_SAMESITE = get_environment_variable(
        cast=str(), name="SESSION_COOKIE_SAMESITE", default="Lax"
    )
    PERMANENT_SESSION_LIFETIME = get_environment_variable(
        cast=int(), name="PERMANENT_SESSION_LIFETIME", default=3600
    )

    # flask-session
    SESSION_TYPE = get_environment_variable(
        cast=str(), name="SESSION_TYPE", default="redis"
    )
    SESSION_KEY_PREFIX = "session:"

    ###############################################################################
    # cache                                                                       #
    ###############################################################################
    REDIS_URL = (
        f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
        if REDIS_PASSWORD
        else f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    )

    ###############################################################################
    # miscellaneous                                                               #
    ###############################################################################
    STRICT_SLASHES = get_environment_variable(
        cast=bool(), name="STRICT_SLASHES", default=False
    )
    MAX_CONTENT_LENGTH = get_environment_variable(
        cast=int(), name="MAX_CONTENT_LENGTH", default=524288
    )

    ###############################################################################
    # Scheduler                                                                   #
    ###############################################################################
    SCHEDULER_TIMEZONE = get_environment_variable(
        cast=str(), name="TIMEZONE", default="UTC"
    )


class FlaskProductionConfig(FlaskBaseConfig):
    """Flask production config."""

    FLASK_ENV = "production"
    FLASK_DEBUG = False
    TESTING = False


class FlaskDevelopmentConfig(FlaskBaseConfig):
    """Flask development config."""

    FLASK_ENV = "development"
    FLASK_DEBUG = True
    TESTING = False


class FlaskTestingConfig(FlaskBaseConfig):
    """Flask testing config."""

    FLASK_ENV = "testing"
    FLASK_DEBUG = True
    TESTING = True
