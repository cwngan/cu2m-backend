from datetime import datetime, timezone
from typing import ClassVar, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic_mongo import PydanticObjectId


class CoreModel(BaseModel):
    model_config = ConfigDict(serialize_by_alias=True)


class PreUser(CoreModel):
    id: Optional[PydanticObjectId] = Field(alias="_id", default=None)
    email: str
    license_key_hash: str
    activated_at: datetime = datetime.fromtimestamp(0, timezone.utc)


class User(PreUser):
    first_name: str
    last_login: datetime
    last_name: str
    major: str
    password_hash: str
    username: str


class UserCreate(CoreModel):
    email: str
    first_name: str
    last_name: str
    major: str
    password: str
    username: str
    license_key: str


class UserRead(CoreModel):
    id: PydanticObjectId = Field(alias="_id")
    email: str
    first_name: str
    last_login: datetime
    last_name: str
    major: str
    username: str


class UserUpdate(CoreModel):
    major: Optional[str] = None
    password: Optional[str] = None
    username: Optional[str] = None
    last_login: Optional[datetime] = None


class Course(CoreModel):
    id: Optional[PydanticObjectId] = Field(alias="_id", default=None)
    code: str
    corequisites: str
    description: str
    is_graded: bool
    not_for_major: str
    not_for_taken: str
    original: str
    parsed: bool
    prerequisites: str
    title: str
    units: float


class SemesterPlan(CoreModel):
    id: Optional[PydanticObjectId] = Field(alias="_id", default=None)
    course_plan_id: PydanticObjectId
    courses: list[str]
    semester: int
    year: int


class CoursePlan(CoreModel):
    id: Optional[PydanticObjectId] = Field(alias="_id", default=None)
    description: str
    favourite: bool
    name: str
    updated_at: datetime
    user_id: Optional[PydanticObjectId]


class CoursePlanRead(CoreModel):
    id: Optional[PydanticObjectId] = Field(alias="_id", default=None)
    description: str
    favourite: bool
    name: str
    updated_at: datetime
    user_id: PydanticObjectId


class CoursePlanCreate(CoreModel):
    description: str
    name: str


class CoursePlanUpdate(CoreModel):
    description: Optional[str] = None
    favourite: Optional[bool] = None
    name: Optional[str] = None
    updated_at: Optional[datetime] = None


class ResetToken(CoreModel):
    TTL: ClassVar[int] = 10 * 60  # 10 minutes

    id: Optional[PydanticObjectId] = Field(alias="_id", default=None)
    username: str
    token_hash: str
    ttl: int = TTL
    expires_at: datetime

    def is_valid(self):
        return datetime.now(timezone.utc) < self.expires_at
