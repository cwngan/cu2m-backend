from pydantic import BaseModel

from flaskr.db.models import UserCreate


class UserCreateRequestModel(BaseModel):
    user: UserCreate


class UserDeleteRequestModel(BaseModel):
    username: str


class UserLoginRequestModel(BaseModel):
    username: str
    password: str
