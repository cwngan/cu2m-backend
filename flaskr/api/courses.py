import re
from flask import Blueprint, request
from flask_pydantic import validate

from bson import ObjectId
from flaskr.api.respmodels import CoursesResponseModel
from flaskr.db.courses import get_all_courses, get_courses
from flaskr.db.models import Course

route = Blueprint("courses", __name__, url_prefix="/courses")


@route.route("/", methods=["GET"])
@validate(response_by_alias=True, exclude_none=True)
def courses():
    patterns = request.args.getlist("code")
    excludes = request.args.getlist("excludes")
    includes = request.args.getlist("includes")
    after = request.args.get("after", default="0" * 24)
    limit = request.args.get("limit", default="100")

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

    # Verify after value
    if not ObjectId.is_valid(after):
        return (
            CoursesResponseModel(status="ERROR", error="Invalid after value."),
            400,
        )
    else:
        after = ObjectId(after)

    # Verify limit value
    if not limit.isdigit() or not (0 < int(limit) < 2**63):
        return (
            CoursesResponseModel(
                status="ERROR",
                error="Invalid limit value (should be a positive 8-byte integer).",
            ),
            400,
        )
    else:
        limit = int(limit)

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
                lambda attr: attr not in ["code", "title", "units"],
                course_attributes,
            )
        )
    elif includes:
        excludes = list(filter(lambda attr: attr not in includes, course_attributes))
    elif set(excludes) == set(course_attributes):
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
    # Must return ID for pagination
    if projection:
        projection["_id"] = True

    courses = None
    if not patterns:
        courses = get_all_courses(projection, after, limit)
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
        courses = get_courses(patterns, projection, after, limit)

    return CoursesResponseModel(data=courses)
