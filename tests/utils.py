from datetime import datetime
from os import urandom

from flaskr.db.models import User


def random_user():
    return User(
        email=urandom(16).hex(),
        username=urandom(16).hex(),
        first_name=urandom(16).hex(),
        last_name=urandom(16).hex(),
        major=urandom(16).hex(),
        password_hash=urandom(16).hex(),
        license_key_hash=urandom(16).hex(),
        last_login=datetime.fromtimestamp(int.from_bytes(urandom(4), "big")),
        activated_at=datetime.fromtimestamp(int.from_bytes(urandom(4), "big")),
    )
