from typing import List, Literal, Optional

from pydantic import BaseModel

from flaskr.api.errors import APIErrors
from flaskr.db.models import Course, CoursePlanRead, SemesterPlanRead, UserRead


class ResponseModel(BaseModel):
    status: Literal["OK", "ERROR"] = "OK"
    error: Optional[APIErrors] = None


class RootResponseModel(ResponseModel):
    data: str = "CU^2M API"


class PingResponseModel(ResponseModel):
    data: str


class HealthResponseModel(ResponseModel):
    data: dict[str, bool]


class CoursesResponseModel(ResponseModel):
    data: Optional[list[Course]] = None


class UserResponseModel(ResponseModel):
    data: UserRead | None = None


class SemesterPlanResponseModel(ResponseModel):
    data: SemesterPlanRead | None = None


class CoursePlanResponseModel(ResponseModel):
    data: CoursePlanRead | list[CoursePlanRead] | None = None


class CoursePlanWithSemestersData(BaseModel):
    course_plan: CoursePlanRead
    semester_plans: List[SemesterPlanRead]


class CoursePlanWithSemestersResponseModel(ResponseModel):
    data: CoursePlanWithSemestersData | None = None
