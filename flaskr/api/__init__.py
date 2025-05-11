from flask import Blueprint
from flask import current_app as app
from flask_pydantic import validate  # type: ignore

from flaskr.api import course_plans, courses, health, ping, semester_plans, user
from flaskr.api.exceptions import NotFound
from flaskr.api.respmodels import RootResponseModel

route = Blueprint("api", __name__, url_prefix="/api")


@route.route("/", methods=["GET"])
@validate()
def root():
    return RootResponseModel()


@route.route("/throw", methods=["GET"])
def throw_error():  # type: ignore
    if app.testing:
        raise Exception("This is a test error")
    raise NotFound(debug_info="Should not be accessed in production")


route.register_blueprint(ping.route)
route.register_blueprint(health.route)
route.register_blueprint(courses.route)
route.register_blueprint(user.route)
route.register_blueprint(course_plans.route)
route.register_blueprint(semester_plans.route)
