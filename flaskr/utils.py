import logging
import secrets
import string
from hashlib import sha256
from argon2 import PasswordHasher as ArgonPasswordHasher

from colorama import Style, Fore, Back


class RequestFormatter(logging.Formatter):
    default_custom_fmt = (
        "{bold}%(asctime)s{reset} [%(levelname)s] - [%(name)s]: %(message)s".format(
            bold=Style.BRIGHT, reset=Style.RESET_ALL
        )
    )

    FORMATS = {
        logging.DEBUG: Fore.WHITE,
        logging.INFO: Fore.CYAN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.WHITE + Back.RED,
    }

    def __init__(
        self, fmt=None, datefmt=None, style="%", validate=True, *, defaults=None
    ):
        super().__init__(
            self.default_custom_fmt, datefmt, style, validate, defaults=defaults
        )

    def format(self, record):
        record.levelname = "{color}{levelname}{reset}".format(
            color=self.FORMATS.get(record.levelno),
            levelname=record.levelname,
            reset=Style.RESET_ALL,
        )
        return super().format(record)


class KeyGenerator:
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
        key_hash = sha256(key.encode() + value.encode())
        return (
            f"{key_hash.hexdigest()}.{value}",
            key,
        )

    @classmethod
    def verify_key(cls, key: str, key_hash: str):
        try:
            expected_hash, value = key_hash.split(".")
            user_hash = sha256(key.encode() + value.encode())
            return user_hash.hexdigest() == expected_hash
        except Exception:
            return False


class PasswordHasher:
    argon = ArgonPasswordHasher()

    @classmethod
    def hash_password(cls, password: str):
        return cls.argon.hash(password)

    @classmethod
    def verify_password(cls, hash: str, password: str):
        return cls.argon.verify(hash, password)


class DataProjection:
    user = {"license_key_hash": False, "password_hash": False}
