import json
import logging
import os
from typing import Any

from flask import Flask, request, Response
from flask.logging import default_handler
from flask_pydantic import ValidationError, validate  # type: ignore

from flaskr import api
from flaskr.api.respmodels import ResponseModel
from flaskr.db.database import init_db
from flaskr.utils import RequestFormatter


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
    # Configure Flask app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev" if app.debug else os.urandom(32),
        FLASK_PYDANTIC_VALIDATION_ERROR_RAISE=True,
    )

    # Initalize logging
    default_handler.setFormatter(RequestFormatter())
    app.logger.setLevel(
        logging.getLevelNamesMapping().get(os.getenv("LOGGING_LEVEL", "INFO"))
    )
    app.logger.info("Logging level: %s", logging.getLevelName(app.logger.level))

    # Test logging color formats during debug mode
    if app.debug:
        for levelname, levelno in logging.getLevelNamesMapping().items():
            app.logger.log(levelno, f"Testing {levelname}...")

    # Initialize database
    init_db()

    # Load test config
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

    @app.after_request
    def logging_request(response: Response):
        app.logger.info(
            '{remote_addr} -> "{method} {endpoint} {protocol}" {status_code}'.format(
                remote_addr=request.remote_addr,
                method=request.method,
                endpoint=request.full_path,
                protocol=request.environ.get("SERVER_PROTOCOL"),
                status_code=response.default_status,
            )
        )
        return response

    app.register_error_handler(ValidationError, validation_error_handler)
    app.register_blueprint(api.route)

    return app
