import os
from typing import Any

from flask import Flask
from flask_pydantic import ValidationError, validate  # type: ignore

from flaskr import api
from flaskr.api.errors import ResponseError
from flaskr.api.respmodels import ResponseModel
from flaskr.db.database import init_db


def validation_error_handler(e: ValidationError):
    return (
        ResponseModel(status="ERROR", error=ResponseError.BadRequest).model_dump(),
        400,
    )


def global_error_handler(e: Exception):
    return (
        ResponseModel(status="ERROR", error=ResponseError.InternalError).model_dump(),
        500,
    )


def create_app(test_config: dict[str, Any] | None = None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev", FLASK_PYDANTIC_VALIDATION_ERROR_RAISE=True
    )

    init_db()

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
    def root():  # type: ignore
        return ResponseModel()

    if app.testing:

        @app.route("/throw", methods=["GET"])
        def throw_error():  # type: ignore
            raise Exception("This is a test error")

    app.register_error_handler(ValidationError, validation_error_handler)
    app.register_error_handler(Exception, global_error_handler)
    app.register_blueprint(api.route)

    return app
