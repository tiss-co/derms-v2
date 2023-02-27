import time
from functools import wraps
from backend.extensions import db
from backend.logger import logger
from backend.extensions import scheduler


def teardown_taskcontext(func):
    """
    A teardown decorator to be run at the end of each task, regardless of whether
    there was an exception or not.

    Notes
    -----
    The task result will be returned. if an Exception occurred, it will be raised.

    """

    @wraps(func)
    def inner(*args, **kwargs):
        with scheduler.app.app_context():
            try:
                return func(*args, **kwargs)
            except Exception:
                logger.error("Task failed.", exc_info=True)
                db.session.rollback()
                db.session.flush()
                raise
            finally:
                db.session.remove()
                db.session.close()  # back to the clean state (still reusable).
                time.sleep(1)

    return inner
