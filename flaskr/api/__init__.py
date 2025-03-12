from flask import Blueprint
from flask_pydantic import validate

from flaskr.models import RootResponseModel
from flaskr.api import ping

route = Blueprint("api", __name__, url_prefix="/api")


@route.route("/", methods=["GET"])
@validate()
def root():
    return RootResponseModel()


route.register_blueprint(ping.route)
