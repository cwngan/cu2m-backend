from flask import Blueprint
from flask_pydantic import validate

from flaskr.api.respmodels import HealthResponseModel
from flaskr.db.database import get_db

route = Blueprint("health", __name__, url_prefix="/health")


@route.route("/", methods=["GET"])
@validate()
def health():
    """
    Check health of the server
    ---

    swagger_from_file: ./docs/health/root.yml
    """
    db = get_db()
    return HealthResponseModel(data={"server": True, "db": db is not None})
