# import logging

from bson import ObjectId
from flask import Blueprint
from flask_pydantic import validate  # type: ignore

from flaskr.api.auth_guard import auth_guard
from flaskr.api.reqmodels import (
    SemesterPlanCreateRequestModel,
    SemesterPlanUpdateRequestModel,
)
from flaskr.api.respmodels import SemesterPlanResponseModel
from flaskr.db.course_plans import get_course_plan  # Corrected the import
from flaskr.db.semester_plans import (
    create_semester_plan,
    delete_semester_plan,
    get_semester_plan,
    update_semester_plan,
)
from flaskr.db.user import User

route = Blueprint("semester_plans", __name__, url_prefix="/semester-plans")


@route.route("/<semester_plan_id>", methods=["GET"])
@auth_guard
@validate(response_by_alias=True)
def get(semester_plan_id):
    """
    Return the SemesterPlan with the specified id.
    """
    if not ObjectId.is_valid(semester_plan_id):
        return (
            SemesterPlanResponseModel(status="ERROR", error="Semester plan not found"),
            404,
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
@auth_guard
@validate(response_by_alias=True)
def post(body: SemesterPlanCreateRequestModel, user: User):
    """
    Create a SemesterPlan with the given parameters.
    """
    # Validate course plan ID
    if not ObjectId.is_valid(body.course_plan_id):
        return (
            SemesterPlanResponseModel(status="ERROR", error="Course plan not found"),
            404,
        )

    course_plan_id = ObjectId(body.course_plan_id)

    # Ensure the course plan exists and belongs to the user
    course_plan = get_course_plan(ObjectId(course_plan_id), user.id)
    if not course_plan:
        return (
            SemesterPlanResponseModel(status="ERROR", error="Course plan not found"),
            404,
        )

    semester_plan = create_semester_plan(
        course_plan_id=course_plan_id, semester=body.semester, year=body.year
    )
    if not semester_plan:
        return (
            SemesterPlanResponseModel(
                status="ERROR",
                error="Semester plan with same semester and year already exists",
            ),
            400,
        )
    return SemesterPlanResponseModel(data=semester_plan.model_dump()), 200


@route.route("/<semester_plan_id>", methods=["PUT"])
@auth_guard
@validate(response_by_alias=True)
def put(semester_plan_id, body: SemesterPlanUpdateRequestModel):
    if not ObjectId.is_valid(semester_plan_id):
        return (
            SemesterPlanResponseModel(status="ERROR", error="Semester plan not found"),
            404,
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
@auth_guard
@validate(response_by_alias=True)
def delete(semester_plan_id):
    if not ObjectId.is_valid(semester_plan_id):
        return (
            SemesterPlanResponseModel(status="ERROR", error="Semester plan not found"),
            404,
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
