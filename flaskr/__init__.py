import os
from flask import Flask
from flask_pydantic import validate

from flaskr.models import ResponseModel 
from flaskr import api


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY="dev")

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # default root response
    @app.route("/", methods=["GET"])
    @validate()
    def root():
        return ResponseModel()

    app.register_blueprint(api.route)

    return app
