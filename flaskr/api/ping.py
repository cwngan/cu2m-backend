from datetime import datetime

from flask import Blueprint
from flask_pydantic import validate  # type: ignore

from flaskr.api.respmodels import PingResponseModel

route = Blueprint("ping", __name__, url_prefix="/ping")


@route.route("/", methods=["GET"])
@validate()
def ping():
    arrival_time = datetime.now()
    return PingResponseModel(
        data=f"Request arrived at {arrival_time.strftime('%d-%m-%Y %H:%M:%S.%f')}"
    )
