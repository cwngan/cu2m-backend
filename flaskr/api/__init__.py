from flask import Blueprint
from flask_pydantic import validate  # type: ignore

from flaskr.api import course_plans, health, ping, user
from flaskr.api.respmodels import RootResponseModel

route = Blueprint("api", __name__, url_prefix="/api")


@route.route("/", methods=["GET"])
@validate()
def root():
    return RootResponseModel()


route.register_blueprint(ping.route)
route.register_blueprint(health.route)
route.register_blueprint(user.route)
route.register_blueprint(course_plans.route)
