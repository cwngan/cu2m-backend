from datetime import datetime

from flask import Blueprint, session, request
from flask_pydantic import validate  # type: ignore

from flaskr.api import email_service
from flaskr.api.exceptions import DuplicateResource, MethodNotAllowed
from flaskr.api.auth_guard import auth_guard
from flaskr.api.exceptions import (
    InternalError,
    InvalidCredentials,
    InvalidLicenseKey,
    InvalidResetToken,
    PreRegistrationNotFound,
    UsernameTaken,
)
from flaskr.api.reqmodels import (
    UserCreateRequestModel,
    UserForgotPasswordModel,
    UserLoginRequestModel,
    UserResetPasswordModel,
    UserVerifyTokenModel,
    LicenseGenerationRequestModel,
)
from flaskr.api.respmodels import (
    ResponseModel,
    UserResponseModel,
    LicenseKeyResponseModel,
)
from flaskr.db.models import User, UserRead, UserUpdate
from flaskr.db.user import (
    activate_user,
    create_reset_token,
    get_precreated_user,
    get_reset_token,
    get_user_by_username,
    update_user,
    create_precreated_user,
)
from flaskr.utils import KeyGenerator, PasswordHasher

route = Blueprint("user", __name__, url_prefix="/user")


# Custom Exception
class InvalidCredential(Exception):
    pass


@route.route("/signup", methods=["POST"])
@validate(response_by_alias=True)
def signup(body: UserCreateRequestModel):
    user_create = body

    # Verify the provided license key against the pre-created record.
    # For example, fetch the pre-created user by email with is_active=False.
    pre_created = get_precreated_user(user_create.email)
    if not pre_created:
        raise PreRegistrationNotFound()

    # Use PasswordHasher to verify provided license key against license_hash
    if not KeyGenerator.verify_key(
        user_create.license_key, pre_created.license_key_hash
    ):
        raise InvalidLicenseKey()

    # Username regex and availability can be handled in reqmodels validation
    if get_user_by_username(user_create.username):
        raise UsernameTaken()

    # Update pre-created record to activate account and update with credentials.
    user = activate_user(pre_created, user_create)
    if not user:
        # this case cannot happen under normal circumstances
        raise InternalError(debug_info="Unexpected Error: User not created")

    session["username"] = user.username
    user_read = UserRead.model_validate(user.model_dump())
    return UserResponseModel(data=user_read), 201


# @route.route("/delete", methods=["DELETE"])
# @validate(response_by_alias=True)
# def delete(body: UserDeleteRequestModel):
#     username = body.username
#     user = delete_user(username)
#     if not user:
#         return (
#             UserResponseModel(status="ERROR", error="The user does not exist."),
#             404,
#         )

#     user_read = UserRead.model_validate(user)
#     return UserResponseModel(data=user_read), 200


@route.route("/login", methods=["POST"])
@validate(response_by_alias=True)
def login(body: UserLoginRequestModel):
    username, password = body.username, body.password
    user = get_user_by_username(username)
    if not user or not PasswordHasher.verify_password(user.password_hash, password):
        raise InvalidCredentials()
    session["username"] = username
    user = update_user(username, UserUpdate(last_login=datetime.now()))
    assert user is not None, "User should be updated successfully."
    user_read = UserRead.model_validate(user.model_dump())
    return UserResponseModel(data=user_read), 200


@route.route("/logout", methods=["POST"])
@validate()
def logout():
    session.pop("username", None)
    return ResponseModel(), 200


@route.route("/me", methods=["GET"])
@auth_guard
@validate(response_by_alias=True)
def me(user: User):
    user_read = UserRead.model_validate(user.model_dump())
    return UserResponseModel(data=user_read), 200


@route.route("/forgot-password", methods=["POST"])
@validate()
def forgot_password(body: UserForgotPasswordModel):
    token, user = create_reset_token(body.email)
    if token and user:
        # Send the reset password token to the user's email.
        email_service.send_reset_password_token(user, token)
    return ResponseModel(), 200


def _verify_token(body: UserVerifyTokenModel):
    try:
        key, hashkey = body.token.split(".")
        token = get_reset_token(hashkey)
        if token and KeyGenerator.verify_key(key, token.token_hash):
            return token
    except ValueError:
        pass
    raise InvalidResetToken()


@route.route("/verify-token", methods=["POST"])
@validate()
def verify_token(body: UserVerifyTokenModel):
    _verify_token(body)
    return ResponseModel(), 200


@route.route("/reset-password", methods=["PUT"])
@validate()
def reset_password(body: UserResetPasswordModel):
    token = _verify_token(body)
    update_user(
        token.username,
        UserUpdate(password=body.password),
    )

    return ResponseModel(), 200


@route.route("/license", methods=["POST"])
@validate()
def generate_license(body: LicenseGenerationRequestModel):
    if request.remote_addr == "127.0.0.1":
        preuser = get_precreated_user(body.email)
        if preuser is None:
            license_key, _ = create_precreated_user(body.email)
            return LicenseKeyResponseModel(data=license_key)
        raise DuplicateResource(debug_info="Duplicat email during creation process")
    raise MethodNotAllowed(
        debug_info="User attempt to access license generation endpoint while the app is running in production"
    )
