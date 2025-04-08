import random
import string
from datetime import datetime
from os import urandom

from flaskr.db.models import User


def random_user():
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
        last_login=datetime.fromtimestamp(int.from_bytes(urandom(4), "big")),
        activated_at=datetime.fromtimestamp(int.from_bytes(urandom(4), "big")),
    )
