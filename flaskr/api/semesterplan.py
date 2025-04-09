from datetime import datetime

from bson import ObjectId
from flask import Blueprint, request, session
from flask_pydantic import validate  # type: ignore

from flaskr.api.reqmodels import (
    SemesterPlanCreateRequestModel,
    SemesterPlanReadRequestModel,
)
from flaskr.api.respmodels import SemesterPlanResponseModel
from flaskr.db.models import SemesterPlanRead, SemesterPlanUpdate
from flaskr.db.semesterplan import create_semester_plan, get_semester_plan
from flaskr.db.user import get_user

route = Blueprint("semester_plans", __name__, url_prefix="/semester_plans")


# Custom Exception
class InvalidCredential(Exception):
    pass


@route.route("/", methods=["GET"])
@validate(response_by_alias=True)
def get():
    """
    Return the SemesterPlan with the specified id.
    """
    username = session.get("username")
    user = get_user(username) if username else None
    if not user:
        return (
            SemesterPlanResponseModel(status="ERROR", error="Unauthorized"),
            401,
        )
    semester_plan_id = request.args.get("id")
    if not ObjectId.is_valid(semester_plan_id):
        return (SemesterPlanResponseModel(status="ERROR", error="Malformed ID"), 400)
    semester_plan = get_semester_plan(semester_plan_id)
    if not semester_plan:
        return (
            SemesterPlanResponseModel(status="ERROR", error="Semester plan not found"),
            404,
        )
    semester_plan_read = SemesterPlanRead.model_validate(semester_plan.model_dump())
    return SemesterPlanResponseModel(data=semester_plan_read)


@route.route("/", methods=["POST"])
@validate(response_by_alias=True)
def post(body: SemesterPlanCreateRequestModel):
    """
    Create a SemesterPlan with the given paramters.
    """
    username = session.get("username")
    user = get_user(username) if username else None
    if not user:
        return (
            SemesterPlanResponseModel(status="ERROR", error="Unauthorized"),
            401,
        )
    semester_plan = create_semester_plan(
        course_plan_id=body.course_plan_id, semester=body.semester, year=body.year
    )
    return SemesterPlanResponseModel(data=semester_plan)
