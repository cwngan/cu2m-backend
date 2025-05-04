from typing import Any, List, Literal, Optional

from pydantic import BaseModel, computed_field

from flaskr.api.APIExceptions import APIExceptions
from flaskr.db.models import Course, CoursePlanRead, SemesterPlanRead, UserRead


class ResponseModel(BaseModel):
    error: Optional[APIExceptions] = None

    @computed_field
    @property
    def status(self) -> Literal["OK", "ERROR"]:
        return "OK" if self.error is None else "ERROR"


class RootResponseModel(ResponseModel):
    data: str = "CU^2M API"


class PingResponseModel(ResponseModel):
    data: str


class HealthResponseModel(ResponseModel):
    data: dict[str, Any]


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
