from flask import Blueprint
from flask_pydantic import validate

from flaskr.api.models import HealthResponseModel
from flaskr.db.database import get_mongo

route = Blueprint("health", __name__, url_prefix="/health")


@route.route("/", methods=["GET"])
@validate()
def health():
    db = get_mongo()
    return HealthResponseModel(data={"server": True, "db": db is not None})
