import logging
import os
import random
import string
from datetime import datetime, timezone
from typing import Any, Callable, TypeAlias

from pymongo.database import Database

from flaskr.db.models import User
from flaskr.utils import RequestFormatter

_pytest_logger: logging.Logger | None = None


def random_user():
    now = int(datetime.now().timestamp())
    return User(
        email=random_string(),
        username="".join(
            random.choices(
                string.ascii_letters + string.digits + "_", k=random.randint(5, 20)
            )
        ),
        first_name="".join(
            random.choices(string.ascii_letters, k=random.randint(2, 20))
        ),
        last_name="".join(
            random.choices(string.ascii_letters, k=random.randint(2, 20))
        ),
        major=random_string(),
        password_hash=random_string(),
        license_key_hash=random_string(),
        last_login=datetime.fromtimestamp(random.randint(0, now), timezone.utc),
        activated_at=datetime.fromtimestamp(random.randint(0, now), timezone.utc),
    )


def random_string(length: int = 10):
    """
    Generate a random string of fixed length.

    :param length: Length of the string to be generated.
    :return: Random string.
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def get_pytest_logger():
    global _pytest_logger
    if not _pytest_logger:
        _pytest_logger = logging.getLogger("pytest")
        _pytest_logger.setLevel(
            logging.getLevelNamesMapping().get(os.getenv("LOGGING_LEVEL", "INFO"))
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(RequestFormatter())
        _pytest_logger.addHandler(console_handler)
    return _pytest_logger


GetDatabase: TypeAlias = Callable[[], Database[dict[str, Any]]]
