# import logging

from bson import ObjectId
from flask import Blueprint, session
from flask_pydantic import validate  # type: ignore

from flaskr.api.reqmodels import (
    SemesterPlanCreateRequestModel,
    SemesterPlanUpdateRequestModel,
)
from flaskr.api.respmodels import SemesterPlanResponseModel
from flaskr.db.semester_plans import (
    create_semester_plan,
    get_semester_plan,
    update_semester_plan,
    delete_semester_plan,
)
from flaskr.db.user import get_user_by_username
from flaskr.db.course_plans import get_course_plan  # Corrected the import


route = Blueprint("semester_plans", __name__, url_prefix="/semester-plans")


@route.route("/<semester_plan_id>", methods=["GET"])
@validate(response_by_alias=True)
def get(semester_plan_id):
    """
    Return the SemesterPlan with the specified id.
    """
    username = session.get("username")
    user = get_user_by_username(username) if username else None
    if not user:
        return (
            SemesterPlanResponseModel(status="ERROR", error="Unauthorized"),
            401,
        )
    if not ObjectId.is_valid(semester_plan_id):
        return (
            SemesterPlanResponseModel(status="ERROR", error="Malformed ID"),
            400,
        )
    semester_plan = get_semester_plan(semester_plan_id)
    if not semester_plan:
        return (
            SemesterPlanResponseModel(status="ERROR", error="Semester plan not found"),
            404,
        )
    return (
        SemesterPlanResponseModel(data=semester_plan.model_dump()),
        200,
    )


@route.route("/", methods=["POST"])
@validate(response_by_alias=True)
def post(body: SemesterPlanCreateRequestModel):
    """
    Create a SemesterPlan with the given parameters.
    """
    username = session.get("username")
    user = get_user_by_username(username) if username else None
    if not user:
        return (
            SemesterPlanResponseModel(status="ERROR", error="Unauthorized"),
            401,
        )

    # Validate and convert course_plan_id
    try:
        course_plan_id = ObjectId(body.course_plan_id)
    except Exception:
        return (
            SemesterPlanResponseModel(status="ERROR", error="Invalid course_plan_id"),
            400,
        )

    # Ensure the course plan exists and belongs to the user
    course_plan = get_course_plan(course_plan_id, user.id)
    if not course_plan:
        return (
            SemesterPlanResponseModel(
                status="ERROR", error="Course plan not found or unauthorized"
            ),
            404,
        )

    semester_plan = create_semester_plan(
        course_plan_id=course_plan_id, semester=body.semester, year=body.year
    )
    return SemesterPlanResponseModel(data=semester_plan.model_dump()), 200


@route.route("/<semester_plan_id>", methods=["PUT"])
@validate(response_by_alias=True)
def put(semester_plan_id, body: SemesterPlanUpdateRequestModel):
    username = session.get("username")
    user = get_user_by_username(username) if username else None
    if not user:
        return (
            SemesterPlanResponseModel(status="ERROR", error="Unauthorized"),
            401,
        )
    if not ObjectId.is_valid(semester_plan_id):
        return (
            SemesterPlanResponseModel(status="ERROR", error="Malformed ID"),
            400,
        )
    updates = body.model_dump(exclude_none=True)
    updated_plan = update_semester_plan(semester_plan_id, updates)
    if not updated_plan:
        return (
            SemesterPlanResponseModel(status="ERROR", error="Semester plan not found"),
            404,
        )
    return (
        SemesterPlanResponseModel(data=updated_plan.model_dump()),
        200,
    )


@route.route("/<semester_plan_id>", methods=["DELETE"])
@validate(response_by_alias=True)
def delete(semester_plan_id):
    username = session.get("username")
    user = get_user_by_username(username) if username else None
    if not user:
        return (
            SemesterPlanResponseModel(status="ERROR", error="Unauthorized"),
            401,
        )
    if not ObjectId.is_valid(semester_plan_id):
        return (
            SemesterPlanResponseModel(status="ERROR", error="Malformed ID"),
            400,
        )
    deleted_plan = delete_semester_plan(semester_plan_id)
    if not deleted_plan:
        return (
            SemesterPlanResponseModel(status="ERROR", error="Semester plan not found"),
            404,
        )
    return (
        SemesterPlanResponseModel(data=deleted_plan.model_dump()),
        200,
    )
