import os
from hashlib import sha256, scrypt
from base64 import b64encode, b64decode

from flaskr.db.models import User, UserCreate


class LicenseKeyGenerator:
    @classmethod
    def generate_new_key(self, user_create: UserCreate):
        key, value = os.urandom(24), os.urandom(24)
        license_key_hash = sha256(user_create.email.encode("ascii") + key + value)
        return (
            f"{license_key_hash.hexdigest()}.{value.hex()}",
            b64encode(key).decode("ascii"),
        )

    @classmethod
    def verify_key(self, user: User, key: str, license_key: str):
        hex_hash, value = license_key.split(".")
        license_key_hash = sha256(
            user.email.encode("ascii") + key + bytes.fromhex(value)
        )
        return license_key_hash.hexdigest() == hex_hash


class PasswordHasher:
    n = 16384
    r = 8
    p = 1

    @classmethod
    def __hash_password(self, password: str, salt: bytes, n: int, r: int, p: int):
        return scrypt(password.encode("ascii"), salt=salt, n=n, r=r, p=p)

    @classmethod
    def hash_password(self, password: str):
        salt = os.urandom(16)
        password_hash = PasswordHasher.__hash_password(
            password, salt, self.n, self.r, self.p
        )
        return f"16384$8$1${b64encode(salt).decode('ascii')}${b64encode(password_hash).decode('ascii')}"

    @classmethod
    def verify_password(self, hash: str, password: str):
        n, r, p, salt, password_hash = hash.split("$")
        return PasswordHasher.__hash_password(
            password, b64decode(salt), n, r, p
        ) == b64decode(password_hash)


class DataProjection:
    user = {"license_key_hash": False, "password_hash": False}
