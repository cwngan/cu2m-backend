import os
from base64 import b64decode, b64encode
from hashlib import scrypt, sha256

from flaskr.db.models import UserCreate


class LicenseKeyGenerator:
    @classmethod
    def generate_new_key(cls, email: str):
        key, value = os.urandom(24), os.urandom(24)
        license_key_hash = sha256(email.encode("ascii") + key + value)
        return (
            f"{license_key_hash.hexdigest()}.{value.hex()}",
            b64encode(key).decode("ascii"),
        )

    @classmethod
    def verify_key(cls, user: UserCreate, license_key_hash: str):
        expected_license_hash, value = license_key_hash.split(".")
        user_license_hash = sha256(
            user.email.encode("ascii")
            + user.license_key.encode("ascii")
            + bytes.fromhex(value)
        )
        return user_license_hash.hexdigest() == expected_license_hash


class PasswordHasher:
    n = 16384
    r = 8
    p = 1

    @classmethod
    def __hash_password(cls, password: str, salt: bytes, n: int, r: int, p: int):
        return scrypt(password.encode("ascii"), salt=salt, n=n, r=r, p=p)

    @classmethod
    def hash_password(cls, password: str):
        salt = os.urandom(16)
        password_hash = PasswordHasher.__hash_password(
            password, salt, cls.n, cls.r, cls.p
        )
        return f"16384$8$1${b64encode(salt).decode('ascii')}${b64encode(password_hash).decode('ascii')}"

    @classmethod
    def verify_password(cls, hash: str, password: str):
        n, r, p, salt, password_hash = hash.split("$")
        n, r, p = int(n), int(r), int(p)
        return PasswordHasher.__hash_password(
            password, b64decode(salt), n, r, p
        ) == b64decode(password_hash)


class DataProjection:
    user = {"license_key_hash": False, "password_hash": False}
