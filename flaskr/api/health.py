from flask import Blueprint
from flask_pydantic import validate

from flaskr.models import HealthResponseModel
from flaskr.db import get_mongo

route = Blueprint("health", __name__, url_prefix="/health")


@route.route("/", methods=["GET"])
@validate()
def health():
    db = get_mongo()
    return HealthResponseModel(data={"server": True, "db": db is not None})


@route.route("/db", methods=["GET"])
@validate()
def health_db():
    db = get_mongo()
    return HealthResponseModel(data={"db": db is not None})
