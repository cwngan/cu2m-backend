from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional


class User(BaseModel):
    id: Optional[ObjectId] = Field(alias="_id", default=None)
    email: str
    first_name: str
    last_login: datetime
    last_name: str
    license_key_hash: str
    major: str
    password_hash: str
    username: str


class Course(BaseModel):
    id: Optional[ObjectId] = Field(alias="_id", default=None)
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
    id: Optional[ObjectId] = Field(alias="_id", default=None)
    course_plan_id: ObjectId
    courses: list[str]
    semester: int
    year: int


class CoursePlan(BaseModel):
    id: Optional[ObjectId] = Field(alias="_id", default=None)
    description: str
    favourite: bool
    name: str
    updated_at: datetime
    user_id: ObjectId
