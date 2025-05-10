from flask import Blueprint, request
from flask_pydantic import validate  # type: ignore

from flaskr.api.exceptions import BadRequest
from flaskr.api.respmodels import CoursesResponseModel
from flaskr.db.courses import get_all_courses, get_courses
from flaskr.db.models import Course

route = Blueprint("courses", __name__, url_prefix="/courses")


@route.route("/", methods=["GET"])
@validate(response_by_alias=True, exclude_none=True)
def courses():
    keywords = request.args.getlist("keywords[]")
    excludes = request.args.getlist("excludes[]")
    includes = request.args.getlist("includes[]")
    page = request.args.get("page", default="1")
    limit = request.args.get("limit", default="100")

    # A flag for frontend developers' convenience sake
    basic = request.args.get("basic")
    if basic and basic.lower() not in ["true", "false"]:
        raise BadRequest(
            debug_info="Basic flag can only be a boolean value (true or false)."
        )
    else:
        basic = bool(basic)

    # A flag for comparing course code only
    strict = request.args.get("strict")
    if strict and strict.lower() not in ["true", "false"]:
        raise BadRequest(
            debug_info="Strict flag can only be a boolean value (true or false)."
        )
    else:
        strict = bool(strict)

    # Verify limit value
    if not limit.isdigit() or not page.isdigit():
        raise BadRequest(
            debug_info="Invalid limit or page value (should be a positive 8-byte integer)."
        )
    else:
        limit, page = int(limit), int(page)

    # Verify page * limit - 1 value
    if not (0 < page < 2**31) or not (0 < limit < 2**31):
        raise BadRequest(debug_info="Invalid page and/or limit value.")

    # Includes and excludes list cannot exist together due to potential conflict
    if includes and excludes:
        raise BadRequest(
            debug_info="You cannot use both includes and excludes argument at the same time."
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
        raise BadRequest(debug_info="You cannot exclude all attributes.")

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
        courses = get_courses(keywords, projection, page, limit, strict)

    return CoursesResponseModel.model_validate(
        {
            "data": courses,
        }
    )
