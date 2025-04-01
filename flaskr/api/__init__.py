from flask import Blueprint
from flask_pydantic import validate

from flaskr.api.respmodels import RootResponseModel
from flaskr.api import ping, health, user

route = Blueprint("api", __name__, url_prefix="/api")


@route.route("/", methods=["GET"])
@validate()
def root():
    return RootResponseModel()


route.register_blueprint(ping.route)
route.register_blueprint(health.route)
route.register_blueprint(user.route)
