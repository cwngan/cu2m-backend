import re
from flask import Blueprint, request
from flask_pydantic import validate

from flaskr.api.respmodels import CoursesResponseModel
from flaskr.db.courses import get_all_courses, get_courses
from flaskr.db.models import Course

route = Blueprint("courses", __name__, url_prefix="/courses")


@route.route("/", methods=["GET"])
@validate(response_by_alias=True)
def courses():
    patterns = request.args.getlist("code")
    excludes = request.args.getlist("excludes")
    includes = request.args.getlist("includes")

    # A flag for frontend developers' convenience sake
    basic = request.args.get("basic")
    if basic and basic.lower() not in ["true", "false"]:
        return (
            CoursesResponseModel(
                status="ERROR",
                error="Basic flag can only be a boolean value (true or false).",
            ),
            400,
        )
    else:
        basic = bool(basic)

    # Includes and excludes list cannot exist together due to potential conflict
    if includes and excludes:
        return (
            CoursesResponseModel(
                status="ERROR",
                error="You cannot use both includes and excludes argument at the same time.",
            ),
            400,
        )

    course_attributes = Course.model_fields.keys()
    # Overrides excludes arguments if lite flag is given
    # Else if includes is not None, then transform it to an excludes list
    if basic:
        excludes = list(
            filter(
                lambda attr: attr not in ["code", "title", "units"], course_attributes
            )
        )
    elif includes:
        excludes = list(filter(lambda attr: attr not in includes, course_attributes))
    elif set(excludes + ["id"]) == set(course_attributes):
        return (
            CoursesResponseModel(
                status="ERROR",
                error="You cannot exclude all attributes.",
            ),
            400,
        )

    # Cleanse all fields to the ones the system accepts
    projection = {
        key.lower(): False
        for key in filter(
            lambda exclude: exclude.lower() in course_attributes, excludes
        )
    }
    # For exclude mode, auto escape ID because it's not quite useful for course fetching
    projection["_id"] = False

    courses = None
    if not patterns:
        courses = get_all_courses(projection)
        return CoursesResponseModel(data=courses)
    else:
        for pattern in patterns:
            if not re.fullmatch(
                "[A-Z]{1,4}|[A-Z]{4}[0-9]{1,4}", pattern, flags=re.IGNORECASE
            ):
                return (
                    CoursesResponseModel(
                        status="ERROR", error="Invalid course code prefix."
                    ),
                    400,
                )
        courses = get_courses(patterns, projection)

    return CoursesResponseModel(data=courses)
