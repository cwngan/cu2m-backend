import logging
import secrets
import string
from hashlib import sha256
from logging import LogRecord
from typing import Any, Literal, Mapping

from argon2 import PasswordHasher as ArgonPasswordHasher
from bson import ObjectId
from colorama import Back, Fore, Style
from pydantic_core import core_schema
from typing_extensions import Annotated


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
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        validate: bool = True,
        *,
        defaults: Mapping[str, Any] | None = None,
    ):
        super().__init__(
            self.default_custom_fmt, datefmt, style, validate, defaults=defaults
        )

    def format(self, record: LogRecord):
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
        try:
            return cls.argon.verify(hash, password)
        except Exception:
            return False


class DataProjection:
    user = {"license_key_hash": False, "password_hash": False}


# copy pasted from pydantic_mongo.fields
class ObjectIdAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        object_id_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ]
        )
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema(
                [core_schema.is_instance_schema(ObjectId), object_id_schema]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                str, when_used="json"  # added when_used="json"
            ),
        )

    @classmethod
    def validate(cls, value: Any):
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid id")

        return ObjectId(value)


PydanticObjectId = Annotated[ObjectId, ObjectIdAnnotation]
