# import logging

from bson import ObjectId
from flask import Blueprint, request, session
from flask_pydantic import validate  # type: ignore

from flaskr.api.reqmodels import (
    SemesterPlanCreateRequestModel,
)
from flaskr.api.respmodels import SemesterPlanResponseModel
from flaskr.db.models import SemesterPlanRead, SemesterPlanUpdate
from flaskr.db.semesterplan import (
    create_semester_plan,
    get_semester_plan,
    update_semester_plan,
    delete_semester_plan,
)
from flaskr.db.user import get_user_by_username
from flaskr.db.course_plans import get_course_plan  # Corrected the import

# Configure logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

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
    user = get_user_by_username(username) if username else None
    if not user:
        return (
            SemesterPlanResponseModel(
                status="ERROR", error="Unauthorized"
            ).model_dump(),
            401,
        )
    semester_plan_id = request.args.get("id")
    if not ObjectId.is_valid(semester_plan_id):
        return (
            SemesterPlanResponseModel(
                status="ERROR", error="Malformed ID"
            ).model_dump(),
            400,
        )
    semester_plan = get_semester_plan(semester_plan_id)
    if not semester_plan:
        return (
            SemesterPlanResponseModel(
                status="ERROR", error="Semester plan not found"
            ).model_dump(),
            404,
        )
    semester_plan_read = SemesterPlanRead.model_validate(semester_plan.model_dump())
    semester_plan_read.created_at = (
        semester_plan.created_at
    )  # Ensure created_at is included
    return (
        SemesterPlanResponseModel(
            status="OK", data=semester_plan_read.model_dump()
        ).model_dump(),
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
    return SemesterPlanResponseModel(data=semester_plan), 200


@route.route("/", methods=["PUT"])
@validate(response_by_alias=True)
def put(body: SemesterPlanUpdate):
    username = session.get("username")
    user = get_user_by_username(username) if username else None
    if not user:
        return (
            SemesterPlanResponseModel(
                status="ERROR", error="Unauthorized"
            ).model_dump(),
            401,
        )
    semester_plan_id = request.args.get("id")
    if not ObjectId.is_valid(semester_plan_id):
        return (
            SemesterPlanResponseModel(
                status="ERROR", error="Malformed ID"
            ).model_dump(),
            400,
        )
    updates = body.model_dump(exclude_none=True)
    # logger.debug(f"Updating semester plan {semester_plan_id} with data: {updates}")
    updated_plan = update_semester_plan(semester_plan_id, updates)
    if not updated_plan:
        return (
            SemesterPlanResponseModel(
                status="ERROR", error="Semester plan not found"
            ).model_dump(),
            404,
        )
    # logger.debug(f"Updated semester plan: {updated_plan.model_dump()}")
    return (
        SemesterPlanResponseModel(
            status="OK", data=updated_plan.model_dump()
        ).model_dump(),
        200,
    )


@route.route("/", methods=["DELETE"])
def delete():
    username = session.get("username")
    user = get_user_by_username(username) if username else None
    if not user:
        return (
            SemesterPlanResponseModel(
                status="ERROR", error="Unauthorized"
            ).model_dump(),
            401,
        )
    semester_plan_id = request.args.get("id")
    if not ObjectId.is_valid(semester_plan_id):
        return (
            SemesterPlanResponseModel(
                status="ERROR", error="Malformed ID"
            ).model_dump(),
            400,
        )
    deleted_plan = delete_semester_plan(semester_plan_id)
    if not deleted_plan:
        return (
            SemesterPlanResponseModel(
                status="ERROR", error="Semester plan not found"
            ).model_dump(),
            404,
        )
    return (
        SemesterPlanResponseModel(
            status="OK", data=deleted_plan.model_dump()
        ).model_dump(),
        200,
    )
