from typing import Literal, Optional

from pydantic import BaseModel

from flaskr.db.models import UserRead


class ResponseModel(BaseModel):
    status: Literal["OK", "ERROR"] = "OK"
    error: Optional[str] = None


class RootResponseModel(ResponseModel):
    data: str = "CU^2M API"


class PingResponseModel(ResponseModel):
    data: str


class HealthResponseModel(ResponseModel):
    data: dict[str, bool]


class UserResponseModel(ResponseModel):
    data: UserRead | None = None
