from flask import Blueprint
from flask_pydantic import validate

from flaskr.api.respmodels import HealthResponseModel
from flaskr.db.database import get_db

route = Blueprint("health", __name__, url_prefix="/health")


@route.route("/", methods=["GET"])
@validate()
def health():
    """
    Check health of the database
    ---
    tags:
      - products
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: Product
          required:
            - name
          properties:
            name:
              type: string
              description: The product's name.
              default: "Guarana"
    responses:
      200:
        description: The product inserted in the database
        schema:
          $ref: '#/definitions/Product'
    """
    db = get_db()
    return HealthResponseModel(data={"server": True, "db": db is not None})
