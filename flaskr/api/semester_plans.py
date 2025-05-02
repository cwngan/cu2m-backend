# import logging

from flask import Blueprint
from flask_pydantic import validate  # type: ignore
from pydantic_mongo import PydanticObjectId

from flaskr.api.auth_guard import auth_guard
from flaskr.api.reqmodels import (
    SemesterPlanCreateRequestModel,
    SemesterPlanUpdateRequestModel,
)
from flaskr.api.respmodels import SemesterPlanResponseModel
from flaskr.db.course_plans import get_course_plan  # Corrected the import
from flaskr.db.models import SemesterPlanRead, User
from flaskr.db.semester_plans import (
    create_semester_plan,
    delete_semester_plan,
    get_semester_plan,
    update_semester_plan,
)

route = Blueprint("semester_plans", __name__, url_prefix="/semester-plans")


@route.route("/<semester_plan_id>", methods=["GET"])
@auth_guard
@validate(response_by_alias=True)
def get_one_semester_plan(semester_plan_id: PydanticObjectId, user: User):
    """
    Return the SemesterPlan with the specified id.
    """
    assert user.id is not None, "User ID will never be None here"
    semester_plan = get_semester_plan(semester_plan_id)

    # Ensure the semester plan exists or the course plan belongs to the user
    if not semester_plan or not get_course_plan(semester_plan.course_plan_id, user.id):
        return (
            SemesterPlanResponseModel(status="ERROR", error="Semester plan not found"),
            404,
        )
    semester_read = SemesterPlanRead.model_construct(**semester_plan.model_dump())
    return SemesterPlanResponseModel(data=semester_read), 200


@route.route("/", methods=["POST"])
@auth_guard
@validate(response_by_alias=True)
def post_one_semester_plan(body: SemesterPlanCreateRequestModel, user: User):
    """
    Create a SemesterPlan with the given parameters.
    """
    assert user.id is not None, "User ID will never be None here"
    # Ensure the course plan exists and belongs to the user
    course_plan = get_course_plan(body.course_plan_id, user.id)
    if not course_plan:
        return (
            SemesterPlanResponseModel(status="ERROR", error="Course plan not found"),
            404,
        )

    semester_plan = create_semester_plan(
        course_plan_id=body.course_plan_id, semester=body.semester, year=body.year
    )
    if not semester_plan:
        return (
            SemesterPlanResponseModel(
                status="ERROR",
                error="Semester plan with same semester and year already exists",
            ),
            400,
        )
    semester_read = SemesterPlanRead.model_construct(**semester_plan.model_dump())
    return SemesterPlanResponseModel(data=semester_read), 200


@route.route("/<semester_plan_id>", methods=["PUT"])
@auth_guard
@validate(response_by_alias=True)
def put_one_semester_plan(
    semester_plan_id: PydanticObjectId, body: SemesterPlanUpdateRequestModel, user: User
):
    assert user.id is not None, "User ID will never be None here"
    # Ensure the semester plan exists or the course plan belongs to the user
    semester_plan = get_semester_plan(semester_plan_id)
    if not semester_plan or not get_course_plan(semester_plan.course_plan_id, user.id):
        return (
            SemesterPlanResponseModel(status="ERROR", error="Semester plan not found"),
            404,
        )

    updated_plan = update_semester_plan(semester_plan_id, body)
    semester_read = (
        SemesterPlanRead.model_construct(**updated_plan.model_dump())
        if updated_plan
        else None
    )
    return SemesterPlanResponseModel(data=semester_read), 200


@route.route("/<semester_plan_id>", methods=["DELETE"])
@auth_guard
@validate(response_by_alias=True)
def delete_one_semester_plan(semester_plan_id: PydanticObjectId, user: User):
    assert user.id is not None, "User ID will never be None here"
    semester_plan = get_semester_plan(semester_plan_id)
    # Ensure the semester plan exists or the course plan belongs to the user
    if not semester_plan or not get_course_plan(semester_plan.course_plan_id, user.id):
        return (
            SemesterPlanResponseModel(status="ERROR", error="Semester plan not found"),
            404,
        )

    deleted_plan = delete_semester_plan(semester_plan_id)
    semester_read = (
        SemesterPlanRead.model_construct(**deleted_plan.model_dump())
        if deleted_plan
        else None
    )

    return SemesterPlanResponseModel(data=semester_read), 200
