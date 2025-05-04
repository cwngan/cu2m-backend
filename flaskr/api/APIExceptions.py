from abc import ABC
from http import HTTPStatus
from typing import Annotated, Any, TypeAlias, Union

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

T = Union["APIException", dict[str, Any]]


class APIException(Exception, ABC):
    """
    Base class for all API errors.
    """

    status_code: HTTPStatus
    message: str

    @property
    def kind(self) -> str:
        return self.__class__.__name__

    def __init__(self, message: str | None = None):
        if message:
            self.message = message
        super().__init__(self.message)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.no_info_plain_validator_function(cls.validate),
            python_schema=core_schema.no_info_plain_validator_function(cls.validate),
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls.to_dict, when_used="json"
            ),
        )

    @classmethod
    def validate(cls, value: T):
        if isinstance(value, cls):
            return value

        if not isinstance(value, dict):
            raise ValueError()

        if value.get("kind") != cls.__name__:
            raise ValueError()

        if not isinstance(value.get("message"), str):
            raise ValueError()

        nw = cls()
        nw.message = value["message"]
        return nw

    @staticmethod
    def to_dict(obj: "APIException"):
        return {
            "message": obj.message,
            "kind": obj.kind,
        }


class ResponseError(APIException, ABC):
    """
    Common API errors.
    """


class Unauthorized(ResponseError):
    status_code = HTTPStatus.UNAUTHORIZED
    message = "Please log in to access this resource"


class NotFound(ResponseError):
    status_code = HTTPStatus.NOT_FOUND
    message = "The requested resource was not found"


class BadRequest(ResponseError):
    status_code = HTTPStatus.BAD_REQUEST
    message = "The request was malformed or invalid"


class DuplicateResource(ResponseError):
    status_code = HTTPStatus.CONFLICT
    message = "A resource with these properties already exists"


class UserAuthErrors(APIException, ABC):
    """
    Authentication and registration errors.
    """


class InvalidCredentials(UserAuthErrors):
    status_code = HTTPStatus.UNAUTHORIZED
    message = "Invalid username or password"


class PreRegistrationNotFound(UserAuthErrors):
    status_code = HTTPStatus.NOT_FOUND
    message = "Pre-registration not found"


class InvalidLicenseKey(UserAuthErrors):
    status_code = HTTPStatus.UNAUTHORIZED
    message = "Invalid license key"


class UsernameTaken(UserAuthErrors):
    status_code = HTTPStatus.CONFLICT
    message = "Username already taken"


class InvalidResetToken(UserAuthErrors):
    status_code = HTTPStatus.UNAUTHORIZED
    message = "Invalid reset token"


class UnionExeptionAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        choices: dict[str, core_schema.CoreSchema] = {
            o.__name__: o.__get_pydantic_core_schema__(o, handler)
            for o in source.__args__
        }
        return core_schema.tagged_union_schema(
            choices,
            discriminator="kind",
            from_attributes=True,
        )


APIExceptions: TypeAlias = Annotated[
    Union[
        Unauthorized,
        NotFound,
        BadRequest,
        DuplicateResource,
        InvalidCredentials,
        PreRegistrationNotFound,
        InvalidLicenseKey,
        UsernameTaken,
        InvalidResetToken,
    ],
    UnionExeptionAnnotation,
]
