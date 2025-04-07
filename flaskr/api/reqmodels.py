import re

from pydantic import BaseModel, field_validator

from flaskr.db.models import UserCreate

USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{5,20}$")
NAME_REGEX = re.compile(r"^[a-zA-Z]{2,20}$")


class UserNameValidator(BaseModel):
    """
    Helper model to validate username format.
    """

    @field_validator("username", check_fields=False)
    @classmethod
    def validate_username(cls, username: str) -> str:
        if not USERNAME_REGEX.match(username):
            raise ValueError(
                "Username must be 5-20 alphanumeric or underscore characters"
            )
        return username


class UserCreateRequestModel(UserCreate, UserNameValidator):
    @field_validator("first_name")
    @classmethod
    def validate_firstname(cls, first_name: str) -> str:
        if not NAME_REGEX.match(first_name) or not NAME_REGEX.match(first_name):
            raise ValueError("Names must contain only letters and be of proper length")
        return first_name


class UserDeleteRequestModel(UserNameValidator):
    username: str


class UserLoginRequestModel(UserNameValidator):
    username: str
    password: str
