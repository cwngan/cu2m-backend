from enum import StrEnum


class ResponseError(StrEnum):
    """
    Common API errors
    """

    Unauthorized = "Please log in to access this resource"
    Forbidden = "You don't have permission to access this resource"

    NotFound = "The requested resource was not found"
    BadRequest = "The request was malformed or invalid"
    DuplicateResource = "A resource with these properties already exists"

    InternalError = "An internal server error occurred."


class UserAuthErrors(StrEnum):
    """
    Authentication and registration errors
    """

    InvalidCredentials = "Invalid username or password"
    PreRegistrationNotFound = "Pre-registration not found"
    InvalidLicenseKey = "Invalid license key"
    UsernameTaken = "Username already taken"
    RegistrationFailed = "Registration failed"

    InvalidResetToken = "Invalid reset token"


APIErrors = ResponseError | UserAuthErrors
