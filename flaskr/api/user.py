from flask import Blueprint, session
from flask_pydantic import validate
from pydantic import ValidationError

from flaskr.api.respmodels import UserResponseModel
from flaskr.api.reqmodels import (
    UserCreateRequestModel,
    UserDeleteRequestModel,
    UserLoginRequestModel,
)
from flaskr.db.crud import create_user, read_user, read_user_full, delete_user, get_precreated_user,activate_user
from flaskr.utils import LicenseKeyGenerator, PasswordHasher
from flaskr.db.models import UserCreate, UserRead


route = Blueprint("user", __name__, url_prefix="/user")


# Custom Exception
class InvalidCredential(Exception):
    pass



@route.route("/register", methods=["POST"])
@validate()
def register(body: UserCreateRequestModel):
    user_create = body.user

    # Verify the provided license key against the pre-created record.
    # For example, fetch the pre-created user by email with is_active=False.
    pre_created = get_precreated_user(user_create.email)
    if not pre_created:
        return UserResponseModel(status="ERROR", error="Pre-registration not found.", data=None), 400

    # Use PasswordHasher to verify provided license key against license_hash
    if not PasswordHasher.verify_password(pre_created["license_hash"], user_create.license_key):
        return UserResponseModel(status="ERROR", error="Invalid license key.", data=None), 400

    # Username regex and availability can be handled in reqmodels validation
    if read_user_full(user_create.username):
        return UserResponseModel(status="ERROR", error="Username already taken.", data=None), 400

    # Hash provided password
    user_create.password_hash = PasswordHasher.hash_password(user_create.password)

    # Update pre-created record to activate account and update with credentials.
    user = activate_user(pre_created, user_create)
    if not user:
        return UserResponseModel(status="ERROR", error="Registration failed.", data=None), 400
    user_read = UserRead(**user)
    return UserResponseModel(data=user_read), 201


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
    try:
        username, password = body.username, body.password
        target_user = read_user_full(username)
        if not target_user or not PasswordHasher.verify_password(
            target_user["password_hash"], password
        ):
            raise InvalidCredential("Invalid username or password.")
        session["username"] = username
        user = read_user(username)
        return UserResponseModel(data=user),200
    except ValidationError as e:
        raise InvalidCredential(str(e))
    except InvalidCredential as e:
        return (UserResponseModel(status="ERROR", error=str(e), data=None), 401)


@route.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    return "", 204
