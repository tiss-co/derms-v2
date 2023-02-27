from backend.extensions import redis
from flask.cli import AppGroup

cache = AppGroup("cache", help="Cache functionality.")


@cache.command("clean")
def clean():
    redis.flushdb()
