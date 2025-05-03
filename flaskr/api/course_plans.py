from bson import ObjectId
from flask import Blueprint
from flask_pydantic import validate  # type: ignore

from flaskr.api.auth_guard import auth_guard
from flaskr.api.reqmodels import (
    CoursePlanCreateRequestModel,
    CoursePlanUpdateRequestModel,
)
from flaskr.api.respmodels import CoursePlanResponseModel
from flaskr.db.course_plans import (
    create_course_plan,
    delete_course_plan,
    get_all_course_plans,
    get_course_plan,
    update_course_plan,
)
from flaskr.db.models import CoursePlanRead, CoursePlanUpdate, User

route = Blueprint("course-plans", __name__, url_prefix="/course-plans")


@route.route("/", methods=["GET"])
@auth_guard
@validate(response_by_alias=True)
def read_all(user: User):
    res = [
        CoursePlanRead.model_validate(plan.model_dump())
        for plan in get_all_course_plans(user.id)
    ]
    return CoursePlanResponseModel(status="OK", data=res), 200


@route.route("/<course_plan_id>", methods=["GET"])
@auth_guard
@validate(response_by_alias=True)
def read_one(course_plan_id: str, user: User):
    if not ObjectId.is_valid(course_plan_id):
        return (
            CoursePlanResponseModel(status="ERROR", error="Malformed ID"),
            400,
        )
    course_plan = get_course_plan(ObjectId(course_plan_id), user.id)
    if not course_plan:
        return (
            CoursePlanResponseModel(status="ERROR", error="Not found"),
            404,
        )
    course_plan_read = CoursePlanRead.model_validate(course_plan.model_dump())
    return (
        CoursePlanResponseModel(status="OK", data=course_plan_read),
        200,
    )


@route.route("/", methods=["POST"])
@auth_guard
@validate(response_by_alias=True)
def create(body: CoursePlanCreateRequestModel, user: User):
    res = create_course_plan(
        description=body.description, name=body.name, user_id=user.id
    )
    if not res:
        return CoursePlanResponseModel(status="ERROR", error="Unknown error"), 500
    course_plan_read = CoursePlanRead.model_validate(res.model_dump())

    # TODO: Initialize semester plans according to the given years

    return (
        CoursePlanResponseModel(status="OK", data=course_plan_read.model_dump()),
        200,
    )


@route.route("/<course_plan_id>", methods=["PATCH"])
@auth_guard
@validate(response_by_alias=True)
def update(course_plan_id: str, body: CoursePlanUpdateRequestModel, user: User):
    if not ObjectId.is_valid(course_plan_id):
        return (
            CoursePlanResponseModel(status="ERROR", error="Malformed course plan ID"),
            400,
        )
    res = update_course_plan(
        course_plan_id=ObjectId(course_plan_id),
        course_plan_update=CoursePlanUpdate.model_validate(
            body.model_dump(exclude_none=True)
        ),
        user_id=user.id,
    )
    if not res:
        return CoursePlanResponseModel(status="ERROR", error="Unknown error"), 500
    course_plan_read = CoursePlanRead.model_validate(res.model_dump())
    return CoursePlanResponseModel(status="OK", data=course_plan_read), 200


@route.route("/<course_plan_id>", methods=["DELETE"])
@auth_guard
@validate(response_by_alias=True)
def delete(course_plan_id: str, user: User):
    if not ObjectId.is_valid(course_plan_id):
        return (
            CoursePlanResponseModel(status="ERROR", error="Malformed course plan ID"),
            400,
        )
    res = delete_course_plan(course_plan_id=ObjectId(course_plan_id), user_id=user.id)
    if not res:
        return CoursePlanResponseModel(status="ERROR", error="Not found"), 404
    return CoursePlanResponseModel(status="OK"), 200
