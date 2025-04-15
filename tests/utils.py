import random
import string
from datetime import datetime, timezone
from os import urandom
from typing import Any, Callable, TypeAlias
from pymongo.database import Database

from flaskr.db.models import User


def random_user():
    now = int(datetime.now().timestamp())
    return User(
        email=urandom(16).hex(),
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
        major=urandom(16).hex(),
        password_hash=urandom(16).hex(),
        license_key_hash=urandom(16).hex(),
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


GetDatabase: TypeAlias = Callable[[], Database[dict[str, Any]]]
