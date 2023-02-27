import os

from backend.configs import UMG_CLIENT_HOST, UMG_CLIENT_SSL
from flask_apscheduler import APScheduler
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from umg import Auth

from backend import configs  # isort:skip

redis = FlaskRedis()

db = SQLAlchemy(
    metadata=MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )
)

migrate = Migrate(
    db=db,
    directory=os.path.join(configs.PROJECT_ROOT, "migrations"),
    compare_type=True,
)

ma = Marshmallow()

auth = Auth(url=UMG_CLIENT_HOST, ssl=UMG_CLIENT_SSL)

scheduler = APScheduler()
