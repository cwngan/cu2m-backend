from flask import Blueprint
from flask_pydantic import validate  # type: ignore

from flaskr.api.auth_guard import auth_guard
from flaskr.api.exceptions import InternalError, NotFound
from flaskr.api.reqmodels import (
    CoursePlanCreateRequestModel,
    CoursePlanUpdateRequestModel,
)
from flaskr.api.respmodels import (
    CoursePlanResponseModel,
    CoursePlanWithSemestersData,
    CoursePlanWithSemestersResponseModel,
)
from flaskr.db.course_plans import (
    create_course_plan,
    delete_course_plan,
    get_all_course_plans,
    get_course_plan,
    update_course_plan,
)
from flaskr.db.models import CoursePlanRead, CoursePlanUpdate, SemesterPlanRead, User
from flaskr.db.semester_plans import get_semester_plans_by_course_plan
from flaskr.utils import PydanticObjectId

route = Blueprint("course-plans", __name__, url_prefix="/course-plans")


@route.route("/", methods=["GET"])
@auth_guard
@validate(response_by_alias=True)
def read_all(user: User):
    assert user.id is not None, "User ID will never be None here"
    res = [
        CoursePlanRead.model_validate(plan.model_dump())
        for plan in get_all_course_plans(user.id)
    ]
    return CoursePlanResponseModel(data=res), 200


@route.route("/<course_plan_id>", methods=["GET"])
@auth_guard
@validate(response_by_alias=True)
def read_one(course_plan_id: PydanticObjectId, user: User):
    assert user.id is not None, "User ID will never be None here"
    course_plan = get_course_plan(course_plan_id, user.id)
    if not course_plan:
        raise NotFound()
    course_plan_read = CoursePlanRead.model_validate(course_plan.model_dump())

    assert course_plan_read.id is not None, "Course plan ID will never be None here"
    semester_plans = get_semester_plans_by_course_plan(course_plan_read.id)
    semester_plans_read = [
        SemesterPlanRead.model_validate(sp.model_dump()) for sp in semester_plans
    ]
    return (
        CoursePlanWithSemestersResponseModel(
            data=CoursePlanWithSemestersData(
                course_plan=course_plan_read,
                semester_plans=semester_plans_read,
            ),
        ),
        200,
    )


@route.route("/", methods=["POST"])
@auth_guard
@validate(response_by_alias=True)
def create(body: CoursePlanCreateRequestModel, user: User):
    assert user.id is not None, "User ID will never be None here"
    res = create_course_plan(
        description=body.description, name=body.name, user_id=user.id
    )
    if not res:
        raise InternalError()
    course_plan_read = CoursePlanRead.model_validate(res.model_dump())
    return (
        CoursePlanResponseModel(data=course_plan_read),
        200,
    )


@route.route("/<course_plan_id>", methods=["PATCH"])
@auth_guard
@validate(response_by_alias=True)
def update(
    course_plan_id: PydanticObjectId, body: CoursePlanUpdateRequestModel, user: User
):
    assert user.id is not None, "User ID will never be None here"
    res = update_course_plan(
        course_plan_id=course_plan_id,
        course_plan_update=CoursePlanUpdate.model_validate(
            body.model_dump(exclude_none=True)
        ),
        user_id=user.id,
    )
    if not res:
        raise InternalError()
    course_plan_read = CoursePlanRead.model_validate(res.model_dump())
    return CoursePlanResponseModel(data=course_plan_read), 200


@route.route("/<course_plan_id>", methods=["DELETE"])
@auth_guard
@validate(response_by_alias=True)
def delete(course_plan_id: PydanticObjectId, user: User):
    assert user.id is not None, "User ID will never be None here"
    res = delete_course_plan(course_plan_id=course_plan_id, user_id=user.id)
    if not res:
        raise NotFound()
    return CoursePlanResponseModel(), 200
