from abc import ABC
from http import HTTPStatus
from typing import Annotated, Any, TypeAlias, Union, get_args

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

T = Union["APIException", dict[str, Any]]


class APIException(Exception, ABC):
    """
    Base class for all API errors.

    Attributes:
        status_code: HTTP status code for the error
        message: User-facing error message
        debug_info: Developer-only debug information, not exposed to API
    """

    status_code: HTTPStatus
    message: str

    @property
    def kind(self) -> str:
        return self.__class__.__name__

    def __init__(
        self,
        message: str | None = None,
        status_code: HTTPStatus | None = None,
        *,
        debug_info: str = "",
    ):
        if ABC in self.__class__.__bases__:
            raise TypeError("Cannot instantiate abstract Exception class")
        if message:
            self.message = message
        if status_code:
            self.status_code = status_code
        self.debug_info = debug_info
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
        if ABC in cls.__bases__:
            raise TypeError("Cannot instantiate abstract Exception class")

        if isinstance(value, cls):
            return value

        if not isinstance(value, dict):
            raise ValueError("Expected a dictionary")

        if value.get("kind") != cls.__name__:
            raise ValueError("Missing kind attribute or wrong kind")

        if not isinstance(value.get("message"), str):
            raise ValueError("Missing message attribute")

        if not isinstance(value.get("status_code"), int):
            raise ValueError("Missing status_code attribute")

        nw = cls(value["message"], value["status_code"])
        return nw

    @staticmethod
    def to_dict(obj: "APIException") -> dict[str, Any]:
        return {
            "message": obj.message,
            "kind": obj.kind,
            "status_code": obj.status_code,
        }

    def __str__(self) -> str:
        err = super().__str__()
        if self.debug_info:
            err += f" ({self.debug_info})"
        return err


class ResponseError(APIException, ABC):
    """
    Common API errors.
    """


class MethodNotAllowed(ResponseError):
    status_code = HTTPStatus.METHOD_NOT_ALLOWED
    message = "The requested method is not allowed for this endpoint"


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


class InternalError(ResponseError):
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    message = "An internal server error occurred"


class UserAuthError(APIException, ABC):
    """
    Authentication and registration errors.
    """


class InvalidCredentials(UserAuthError):
    status_code = HTTPStatus.UNAUTHORIZED
    message = "Invalid username or password"


class PreRegistrationNotFound(UserAuthError):
    status_code = HTTPStatus.NOT_FOUND
    message = "Pre-registration not found"


class InvalidLicenseKey(UserAuthError):
    status_code = HTTPStatus.UNAUTHORIZED
    message = "Invalid license key"


class UsernameTaken(UserAuthError):
    status_code = HTTPStatus.CONFLICT
    message = "Username already taken"


class InvalidResetToken(UserAuthError):
    status_code = HTTPStatus.UNAUTHORIZED
    message = "Invalid reset token"


class UnionExeptionAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        choices: dict[str, core_schema.CoreSchema] = {
            o.__name__: o.__get_pydantic_core_schema__(o, handler)
            for o in get_args(source)
            if ABC not in o.__bases__
        }
        return core_schema.tagged_union_schema(
            choices,
            discriminator="kind",
            from_attributes=True,
        )


APIExceptions: TypeAlias = Annotated[
    Union[
        APIException,
        UserAuthError,
        ResponseError,
        MethodNotAllowed,
        Unauthorized,
        NotFound,
        BadRequest,
        DuplicateResource,
        InternalError,
        InvalidCredentials,
        PreRegistrationNotFound,
        InvalidLicenseKey,
        UsernameTaken,
        InvalidResetToken,
    ],
    UnionExeptionAnnotation,
]
