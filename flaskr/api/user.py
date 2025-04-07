from flask import Blueprint, session
from flask_pydantic import validate  # type: ignore

from flaskr.api.reqmodels import (
    UserCreateRequestModel,
    UserDeleteRequestModel,
    UserLoginRequestModel,
)
from flaskr.api.respmodels import UserResponseModel
from flaskr.db.crud import activate_user, delete_user, get_precreated_user, read_user
from flaskr.db.models import UserRead
from flaskr.utils import LicenseKeyGenerator, PasswordHasher

route = Blueprint("user", __name__, url_prefix="/user")


# Custom Exception
class InvalidCredential(Exception):
    pass


@route.route("/register", methods=["POST"])
@validate()
def register(body: UserCreateRequestModel):
    user_create = body

    # Verify the provided license key against the pre-created record.
    # For example, fetch the pre-created user by email with is_active=False.
    pre_created = get_precreated_user(user_create.email)
    if not pre_created:
        return (
            UserResponseModel(status="ERROR", error="Pre-registration not found."),
            400,
        )

    # Use PasswordHasher to verify provided license key against license_hash
    if not LicenseKeyGenerator.verify_key(user_create, pre_created.license_key_hash):
        return (
            UserResponseModel(status="ERROR", error="Invalid license key."),
            400,
        )

    # Username regex and availability can be handled in reqmodels validation
    if read_user(user_create.username):
        return (
            UserResponseModel(status="ERROR", error="Username already taken."),
            400,
        )

    # Update pre-created record to activate account and update with credentials.
    user = activate_user(pre_created, user_create)
    if not user:
        return (
            UserResponseModel(status="ERROR", error="Registration failed."),
            400,
        )

    user_read = UserRead.model_validate(user)
    return UserResponseModel(data=user_read), 201


@route.route("/delete", methods=["DELETE"])
@validate()
def delete(body: UserDeleteRequestModel):
    username = body.username
    user = delete_user(username)
    if not user:
        return (
            UserResponseModel(status="ERROR", error="The user does not exist."),
            404,
        )

    user_read = UserRead.model_validate(user)
    return UserResponseModel(data=user_read), 200


@route.route("/login", methods=["POST"])
@validate()
def login(body: UserLoginRequestModel):
    try:
        username, password = body.username, body.password
        user = read_user(username)
        if not user or not PasswordHasher.verify_password(
            user.password_hash, password
        ):
            raise InvalidCredential("Invalid username or password.")
        session["username"] = username
        user_read = UserRead.model_validate(user)
        return UserResponseModel(data=user_read), 200
    except InvalidCredential as e:
        return (UserResponseModel(status="ERROR", error=str(e)), 401)


@route.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    return "", 204
