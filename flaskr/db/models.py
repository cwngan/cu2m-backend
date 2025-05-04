from datetime import datetime, timezone
from typing import Any, ClassVar, Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import core_schema
from typing_extensions import Annotated


# copy pasted from pydantic_mongo.fields
class ObjectIdAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        object_id_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ]
        )
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema(
                [core_schema.is_instance_schema(ObjectId), object_id_schema]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                str, when_used="json"  # added when_used="json"
            ),
        )

    @classmethod
    def validate(cls, value: Any):
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid id")

        return ObjectId(value)


PydanticObjectId = Annotated[ObjectId, ObjectIdAnnotation]


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
    semester: int = Field(ge=1, le=3)
    year: int
    created_at: datetime


class SemesterPlanRead(CoreModel):
    id: Optional[PydanticObjectId] = Field(alias="_id", default=None)
    course_plan_id: PydanticObjectId
    courses: list[str]
    semester: int = Field(ge=1, le=3)
    year: int
    created_at: datetime


class SemesterPlanCreate(CoreModel):
    course_plan_id: PydanticObjectId
    semester: int = Field(ge=1, le=3)
    year: int


class SemesterPlanUpdate(CoreModel):
    courses: Optional[list[str]] = None
    semester: Optional[int] = Field(ge=1, le=3, default=None)
    year: Optional[int] = None


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
    year: int


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
