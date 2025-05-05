from flask import Blueprint, request
from flask_pydantic import validate

from flaskr.api.respmodels import CoursesResponseModel
from flaskr.db.courses import get_courses, get_all_courses
from flaskr.db.models import Course

route = Blueprint("courses", __name__, url_prefix="/courses")


@route.route("/", methods=["GET"])
@validate(response_by_alias=True, exclude_none=True)
def courses():
    keywords = request.args.getlist("keywords")
    excludes = request.args.getlist("excludes")
    includes = request.args.getlist("includes")
    page = request.args.get("page", default="1")
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

    # Verify page value
    if not page.isdigit() or not (0 < int(page) < 2**63 // limit):
        return (
            CoursesResponseModel(status="ERROR", error="Invalid page value."),
            400,
        )
    else:
        page = int(page)

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
    if not keywords:
        courses = get_all_courses(projection, page, limit)
    else:
        courses = get_courses(keywords, projection, page, limit)

    return CoursesResponseModel(data=courses)
