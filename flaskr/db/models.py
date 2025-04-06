from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId


class User(BaseModel):
    id: Optional[PydanticObjectId] = Field(alias="_id", default=None)
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
    major: str
    password: str
    username: str
    license_key: str
    password_hash: Optional[str] = None  # Add this field


class UserRead(BaseModel):
    id: PydanticObjectId = Field(alias="_id", default=None)
    email: str
    first_name: str
    last_login: datetime
    last_name: str
    major: str
    username: str


class UserUpdate(BaseModel):
    major: str
    password: str
    username: str


class Course(BaseModel):
    id: Optional[PydanticObjectId] = Field(alias="_id", default=None)
    code: str
    corequisites: str
    description: str
    is_graded: bool
    not_for_major: str
    not_for_taken: str
    prerequisites: str
    title: str
    units: str


class SemesterPlan(BaseModel):
    id: Optional[PydanticObjectId] = Field(alias="_id", default=None)
    course_plan_id: PydanticObjectId
    courses: list[str]
    semester: int
    year: int


class CoursePlan(BaseModel):
    id: Optional[PydanticObjectId] = Field(alias="_id", default=None)
    description: str
    favourite: bool
    name: str
    updated_at: datetime
    user_id: PydanticObjectId
