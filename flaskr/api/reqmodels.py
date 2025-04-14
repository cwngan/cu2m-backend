import re

# from flask_pydantic import ValidationError
from pydantic import BaseModel, ValidationError, field_validator
from pydantic_core import PydanticCustomError

from flaskr.db.models import UserCreate

USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{5,20}$")
NAME_REGEX = re.compile(r"^[a-zA-Z]{2,20}$")


class UserNameValidator(BaseModel):
    """
    Helper model to validate username format.
    """

    @field_validator("username", check_fields=False, mode="before")
    def validate_username(cls, username: str) -> str:
        if not USERNAME_REGEX.match(username):
            raise ValidationError.from_exception_data(
                title="validation_error",
                line_errors=[
                    {
                        "type": PydanticCustomError(
                            "value_error",
                            "Username must be 5-20 alphanumeric or underscore characters",
                        ),
                        "input": username,
                    }
                ],
            )
        return username


class UserCreateRequestModel(UserCreate, UserNameValidator):
    @field_validator("first_name", mode="before")
    def validate_firstname(cls, first_name: str) -> str:
        if not NAME_REGEX.match(first_name) or not NAME_REGEX.match(first_name):
            raise ValidationError.from_exception_data(
                title="validation_error",
                line_errors=[
                    {
                        "type": PydanticCustomError(
                            "value_error",
                            "Names must contain only letters and be of proper length",
                        ),
                        "input": first_name,
                    }
                ],
            )
        return first_name


class UserDeleteRequestModel(UserNameValidator):
    username: str


class UserLoginRequestModel(UserNameValidator):
    username: str
    password: str


class UserForgotPasswordModel(BaseModel):
    email: str


class UserVerifyTokenModel(BaseModel):
    username: str
    token: str


class UserResetPasswordModel(UserVerifyTokenModel):
    password: str
