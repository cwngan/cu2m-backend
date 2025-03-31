from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel


class User(BaseModel):
    _id: ObjectId
    email: str
    first_name: str
    last_login: datetime
    last_name: str
    license_key_hash: str
    major: str
    password_hash: str
    username: str


class UserCreate(BaseModel):
    email: str
    first_name: str
    last_name: str
    license_key: str
    major: str
    password: str
    username: str
