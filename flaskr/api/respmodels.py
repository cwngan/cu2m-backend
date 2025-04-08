from typing import Literal, Optional

<<<<<<< HEAD
from flaskr.db.models import Course
=======
from pydantic import BaseModel

from flaskr.db.models import UserRead
>>>>>>> main


class ResponseModel(BaseModel):
    status: Literal["OK", "ERROR"] = "OK"
    error: Optional[str] = None


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
