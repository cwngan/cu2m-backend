from abc import ABC
from http import HTTPStatus


class APIException(Exception, ABC):
    """
    Base class for all API errors.
    """

    status_code: HTTPStatus
    message: str


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
