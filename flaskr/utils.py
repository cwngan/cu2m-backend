import os
import secrets
import string
from base64 import b64decode, b64encode
from hashlib import scrypt, sha256

from flaskr.db.models import UserCreate


class LicenseKeyGenerator:
    charset: str = string.digits + string.ascii_uppercase

    @classmethod
    def __generate_subkey(cls, size: int):
        subkeys: list[str] = []
        for _ in range(size):
            subkey = "".join(secrets.choice(cls.charset) for _ in range(4))
            subkeys.append(subkey)
        return "-".join(subkeys)

    @classmethod
    def generate_new_key(cls):
        key, value = cls.__generate_subkey(4), cls.__generate_subkey(2)
        license_key_hash = sha256(key.encode() + value.encode())
        return (
            f"{license_key_hash.hexdigest()}.{value}",
            key,
        )

    @classmethod
    def verify_key(cls, user: UserCreate, license_key_hash: str):
        try:
            expected_license_hash, value = license_key_hash.split(".")
            user_license_hash = sha256(user.license_key.encode() + value.encode())
            return user_license_hash.hexdigest() == expected_license_hash
        except:
            return False


class PasswordHasher:
    n = 16384
    r = 8
    p = 1

    @classmethod
    def __hash_password(cls, password: str, salt: bytes, n: int, r: int, p: int):
        return scrypt(password.encode("ascii"), salt=b64encode(salt), n=n, r=r, p=p)

    @classmethod
    def hash_password(cls, password: str):
        salt = os.urandom(16)
        password_hash = cls.__hash_password(password, salt, cls.n, cls.r, cls.p)
        return f"16384$8$1${b64encode(salt).decode('ascii')}${b64encode(password_hash).decode('ascii')}"

    @classmethod
    def verify_password(cls, hash: str, password: str):
        try:
            n, r, p, salt, password_hash = hash.split("$")
            n, r, p = int(n), int(r), int(p)
            return cls.__hash_password(
                password, b64decode(salt.encode("ascii")), n, r, p
            ) == b64decode(password_hash.encode("ascii"))
        except:
            return False


class DataProjection:
    user = {"license_key_hash": False, "password_hash": False}
