import json
import os
from typing import Any

from flask import Flask
from flask_pydantic import ValidationError, validate  # type: ignore
from flask_swagger_ui import get_swaggerui_blueprint

from flaskr import api
from flaskr.api.respmodels import ResponseModel
from flaskr.db.database import init_db


def validation_error_handler(e: ValidationError):
    errs: list[list[dict[Any, Any]] | None] = [
        e.body_params,  # type: ignore
        e.form_params,  # type: ignore
        e.query_params,  # type: ignore
        e.path_params,  # type: ignore
    ]
    err = None
    for err_list in errs:
        if err_list is not None:
            err = err_list
            break
    return (
        ResponseModel(
            status="ERROR",
            error=json.dumps(err),
        ).model_dump(),
        400,
    )


def create_app(test_config: dict[str, Any] | None = None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev", FLASK_PYDANTIC_VALIDATION_ERROR_RAISE=True
    )
    swaggerui_blueprint = get_swaggerui_blueprint(
        "/api/docs",
        "/api/spec",
        config={"app_name": "Test application"},  # Swagger UI config overrides
    )
    app.register_blueprint(swaggerui_blueprint)

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

    app.register_error_handler(ValidationError, validation_error_handler)
    app.register_blueprint(api.route)

    return app
