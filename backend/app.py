import sys

from flask import Flask, session
from backend import configs
from backend.extensions import db
from backend.logger import logger
from backend.magic import (
    get_blueprints,
    get_commands,
    get_extensions,
    get_models,
    get_serializers,
)
from flask_cors import CORS


def create_app():
    """Creates a pre-configured Flask application.

    Defaults to using ```backend.configs.FlaskProductionConfig```, unless the
    ```FLASK_DEBUG``` environment variable is explicitly set to ```true```,
    in which case it uses ```backend.configs.FlaskDevelopmentConfig```. Also
    configures paths for the templates folder and static files.

    Returns
    -------
    flask.Flask
        A Flask application.
    """

    return _create_app(
        config_object=(
            configs.FlaskDevelopmentConfig
            if configs.get_environment_variable(
                cast=bool(), name="FLASK_DEBUG", default=False
            )
            else configs.FlaskProductionConfig
        ),
        template_folder=configs.TEMPLATE_FOLDER,
        static_folder=configs.STATIC_FOLDER,
        static_url_path=configs.STATIC_URL_PATH,
    )


def _create_app(config_object: object = configs.FlaskProductionConfig, **kwargs) -> Flask:
    """Creates a Flask application.

    Parameters
    ----------
    config_object : object, optional
        The configuration object to use, defaults to ```backend.configs.FlaskProductionConfig```.
    **kwargs
        Additional keyword arguments to pass to the Flask application.

    Returns
    -------
    flask.Flask
        A Flask application.
    """
    # WARNING: DO NOT FUCK WITH THE ORDER OF THESE CALLS or nightmares will ensue.

    app = Flask(__name__, **kwargs)
    CORS(app)
    configure_app(app=app, config_object=config_object)

    extensions = dict(get_extensions(configs.EXTENSIONS))
    register_extensions(app, extensions)

    blueprints = dict(get_blueprints())
    register_blueprints(app, blueprints)

    # Register all models declared in ```backend/models```
    models = dict(get_models())
    app.models = models

    # Register all serializers declared in ```backend/serializers```
    serializers = dict(get_serializers())
    app.serializers = serializers

    # register cli commands
    commands = dict(get_commands())
    register_cli_commands(app, commands)

    # register shell context
    register_shell_context(app, extensions)

    return app


def configure_app(
        app: Flask, config_object: object = configs.FlaskProductionConfig
) -> None:
    """
    General application configurations:
        - register the app's config.
        - register Jinja extensions if needed.
        - register functions to run on before/after request.
        - etc.

    Parameters
    ----------
    app : flask.Flask
        The Flask application to configure.
    config_object : object, optional
        The configuration object to use, defaults to ```backend.configs.FlaskProductionConfig```.

    Returns
    -------
    None
    """

    app.config.from_object(config_object)

    @app.before_request
    def enable_session_timeout():
        session.permanent = True  # set session to use PERMANENT_SESSION_LIFETIME
        session.modified = True  # reset the session timer on every request

    # @app.after_request
    # def set_csrf_cookie(response):
    #     if response:
    #         response.set_cookie("csrf_token", generate_csrf())
    #     return response

    @app.teardown_request
    def teardown_request(exception):
        # (help: https://stackoverflow.com/a/33284980)
        # (help: https://www.learndatasci.com/tutorials/using-databases-python-postgres-sqlalchemy-and-alembic)
        if exception:
            db.session.rollback()
            db.session.flush()
        db.session.remove()
        db.session.close()


def register_extensions(app: Flask, extensions: dict) -> None:
    """Register and initialize extensions."""

    for extension in extensions.values():
        extension.init_app(app)


def register_blueprints(app: Flask, blueprints: dict) -> None:
    """Register all blueprints declared in ```backend/extensions/blueprints```"""

    # disable strict_slashes on all routes by default
    if not app.config.get("STRICT_SLASHES", False):
        app.url_map.strict_slashes = False

    # register blueprints
    for blueprint in blueprints.values():
        # rstrip '/' off url_prefix because views should be declaring their
        # routes beginning with '/', and if url_prefix ends with '/', routes
        # will end up looking like '/prefix//endpoint', which is no good
        url_prefix = (blueprint.url_prefix or "").rstrip("/")
        app.register_blueprint(blueprint, url_prefix=url_prefix)


def register_cli_commands(app: Flask, commands: dict = {}) -> None:
    """Register all the Click commands declared in ```backend/commands```"""

    for name, command in commands.items():
        if name in app.cli.commands:
            logger.error(f'Command name conflict: "{name}" is taken.')
            sys.exit(1)
        app.cli.add_command(command)


def register_shell_context(app, extensions):
    """Register variables to automatically import when running ```flask shell```."""

    def shell_context():
        ctx = {}
        ctx.update(extensions)
        ctx.update(app.models)
        ctx.update(app.serializers)
        return ctx

    app.shell_context_processor(shell_context)
