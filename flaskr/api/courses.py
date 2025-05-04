import re

from flask import Blueprint, request
from flask_pydantic import validate  # type: ignore

from flaskr.api.APIExceptions import BadRequest
from flaskr.api.respmodels import CoursesResponseModel
from flaskr.db.courses import get_all_courses, get_courses

route = Blueprint("courses", __name__, url_prefix="/courses")


@route.route("/", methods=["GET"])
@validate(response_by_alias=True)
def courses():
    patterns = request.args.getlist("code")
    if not patterns:
        courses = get_all_courses()
        return CoursesResponseModel(data=courses)
    else:
        for pattern in patterns:
            if not re.fullmatch(
                "[A-Z]{1,4}|[A-Z]{4}[0-9]{1,4}", pattern, flags=re.IGNORECASE
            ):
                raise BadRequest()
        courses = get_courses(patterns)
        return CoursesResponseModel(data=courses)
