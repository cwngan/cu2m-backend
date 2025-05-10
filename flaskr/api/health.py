from flask import Blueprint
from flask_pydantic import validate  # type: ignore

from flaskr.api.respmodels import HealthResponseModel
from flaskr.db.database import get_db

route = Blueprint("health", __name__, url_prefix="/health")


@route.route("/", methods=["GET"])
@validate()
def health():
    db = get_db()
    return HealthResponseModel(data={"server": True, "db": db is not None}) # type: ignore
