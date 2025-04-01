from flask import Blueprint, session
from flask_pydantic import validate

from flaskr.api.respmodels import UserResponseModel
from flaskr.api.reqmodels import (
    UserCreateRequestModel,
    UserDeleteRequestModel,
    UserLoginRequestModel,
)
from flaskr.db.crud import create_user, read_user, read_user_full, delete_user
from flaskr.utils import LicenseKeyGenerator, PasswordHasher


route = Blueprint("user", __name__, url_prefix="/user")


@route.route("/register", methods=["POST"])
@validate()
def register(body: UserCreateRequestModel):
    user_create = body.user
    license_key_hash, key = LicenseKeyGenerator.generate_new_key(user_create)
    # TODO: Send the key to the user through
    user = create_user(user_create, license_key_hash)
    if not user:
        return (
            UserResponseModel(
                status="ERROR", error="The username has already been used."
            ),
            400,
        )
    return UserResponseModel(data=user), 201


@route.route("/delete", methods=["DELETE"])
@validate()
def delete(body: UserDeleteRequestModel):
    username = body.username
    user = delete_user(username)
    if not user:
        return UserResponseModel(status="ERROR", error="The user does not exist."), 404
    return UserResponseModel(data=delete_user(username))


@route.route("/login", methods=["POST"])
@validate()
def login(body: UserLoginRequestModel):
    username, password = body.username, body.password
    target_user = read_user_full(username)
    if not target_user or not PasswordHasher.verify_password(
        target_user.password_hash, password
    ):
        return (
            UserResponseModel(status="ERROR", error="Invalid username or password."),
            401,
        )
    session["username"] = username
    return read_user(username)


@route.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    return "", 204
