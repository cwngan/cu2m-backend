from pydantic import BaseModel

from flaskr.db.models import UserCreate
import re

USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{5,20}$")
NAME_REGEX = re.compile(r"^[a-zA-Z]{2,20}$")

class UserCreateRequestModel(BaseModel):
    user: UserCreate
    def validate_user(cls, user):
        if not USERNAME_REGEX.match(user.username):
            raise ValueError("Username must be 5-20 alphanumeric or underscore characters")
        if not NAME_REGEX.match(user.first_name) or not NAME_REGEX.match(user.last_name):
            raise ValueError("Names must contain only letters and be of proper length")
        return user


class UserDeleteRequestModel(BaseModel):
    username: str


class UserLoginRequestModel(BaseModel):
    username: str
    password: str
