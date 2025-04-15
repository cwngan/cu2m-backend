from flask import Blueprint, jsonify, current_app
from flask_pydantic import validate  # type: ignore
from flask_swagger import swagger

from flaskr.api import health, ping, user, courses, course_plans
from flaskr.api.respmodels import RootResponseModel


route = Blueprint("api", __name__, url_prefix="/api")


@route.route("/", methods=["GET"])
@validate()
def root():
    return RootResponseModel()


@route.route("/spec")
def spec():
    return jsonify(swagger(current_app))


route.register_blueprint(ping.route)
route.register_blueprint(health.route)
route.register_blueprint(courses.route)
route.register_blueprint(user.route)
route.register_blueprint(course_plans.route)
