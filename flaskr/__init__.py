import logging
import os
from typing import Any

from flask import Flask, Response, current_app, request
from flask.logging import default_handler
from flask_pydantic import ValidationError, validate  # type: ignore
from werkzeug import exceptions

from flaskr import api
from flaskr.api.exceptions import (
    APIException,
    BadRequest,
    InternalError,
    MethodNotAllowed,
    NotFound,
)
from flaskr.api.respmodels import ResponseModel
from flaskr.db.database import init_db
from flaskr.utils import RequestFormatter


def exception_handler(e: Exception):
    try:
        # Map exceptions from Flask
        if isinstance(e, exceptions.NotFound):
            raise NotFound(debug_info="An undefined api path was requested") from e
        if isinstance(e, exceptions.MethodNotAllowed):
            raise MethodNotAllowed() from e

        # Errors by Flask-Pydantic
        if isinstance(e, ValidationError):
            raise BadRequest(debug_info="Pydantic validation error") from e

        # Errors thrown by the app
        if isinstance(e, APIException):
            raise e

        # unhandled exceptions
        raise InternalError(debug_info="An unhandled exception has occured") from e

    except APIException as e:
        if isinstance(e, InternalError):
            current_app.logger.exception(e)
        else:
            current_app.logger.warning(e, exc_info=True)

        return ResponseModel(error=e).model_dump(mode="json"), e.status_code


def create_app(test_config: dict[str, Any] | None = None):
    app = Flask(__name__, instance_relative_config=True)

    # Load test config
    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    # Initalize logging
    default_handler.setFormatter(RequestFormatter())
    app.logger.setLevel(
        logging.getLevelNamesMapping().get(os.getenv("LOGGING_LEVEL", "INFO"))  # type: ignore
    )
    app.logger.info("Logging level: %s", logging.getLevelName(app.logger.level))

    # Configure Flask app
    secret_key = "dev" if app.debug or app.testing else os.getenv("SECRET_KEY")
    if secret_key is None:
        app.logger.critical("Flask secret key is not set. Exiting.")
        exit(0)
    app.config.from_mapping(
        SECRET_KEY=secret_key,
        FLASK_PYDANTIC_VALIDATION_ERROR_RAISE=True,
    )

    # Test logging color formats during debug mode
    if app.debug:
        for levelname, levelno in logging.getLevelNamesMapping().items():
            app.logger.log(levelno, f"Testing {levelname}...")

    # Initialize database
    init_db()

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
    def logging_request(response: Response):  # type: ignore
        app.logger.debug(
            '{remote_addr} -> "{method} {endpoint} {protocol}" {status_code}'.format(
                remote_addr=request.remote_addr,
                method=request.method,
                endpoint=request.full_path,
                protocol=request.environ.get("SERVER_PROTOCOL"),
                status_code=response.default_status,
            )
        )
        return response

    app.register_error_handler(Exception, exception_handler)
    app.register_blueprint(api.route)

    return app
