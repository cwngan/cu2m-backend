from flask import Blueprint
from flask_pydantic import validate  # type: ignore

from flaskr.api import health, ping, user, courses, course_plans, semester_plans
from flaskr.api.respmodels import RootResponseModel

route = Blueprint("api", __name__, url_prefix="/api")


@route.route("/", methods=["GET"])
@validate()
def root():
    return RootResponseModel()


route.register_blueprint(ping.route)
route.register_blueprint(health.route)
route.register_blueprint(courses.route)
route.register_blueprint(user.route)
route.register_blueprint(course_plans.route)
route.register_blueprint(semester_plans.route)
