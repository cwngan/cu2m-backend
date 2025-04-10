import os
from flask import Blueprint, current_app, jsonify
from flask_pydantic import validate  # type: ignore
from flask_swagger import swagger

from flaskr.api import health, ping, user, docs
from flaskr.api.respmodels import RootResponseModel

route = Blueprint("api", __name__, url_prefix="/api")


@route.route("/", methods=["GET"])
@validate()
def root():
    return RootResponseModel()


@route.route("/spec", methods=["GET"])
def spec():
    return jsonify(swagger(current_app))


route.register_blueprint(ping.route)
route.register_blueprint(health.route)
route.register_blueprint(user.route)
route.register_blueprint(docs.route)
