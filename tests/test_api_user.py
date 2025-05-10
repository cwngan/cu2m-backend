from flask.testing import FlaskClient
from pytest import MonkeyPatch
from werkzeug.test import TestResponse

from flaskr.api.exceptions import (
    BadRequest,
    InvalidCredentials,
    InvalidLicenseKey,
    InvalidResetToken,
    PreRegistrationNotFound,
    Unauthorized,
    UsernameTaken,
)
from flaskr.api.reqmodels import (
    UserForgotPasswordModel,
    UserLoginRequestModel,
    UserResetPasswordModel,
    UserVerifyTokenModel,
)
from flaskr.api.respmodels import ResponseModel, UserResponseModel
from flaskr.db.models import User, UserCreate, UserRead
from flaskr.db.user import create_precreated_user
from tests.utils import GetDatabase, random_user


def test_signup(client: FlaskClient):
    TEST_USER = random_user()

    def _send_request(usr: User, key: str):
        user_create = UserCreate.model_validate(
            {
                **usr.model_dump(mode="json"),
                "license_key": key,
                "password": usr.password_hash,
            }
        )

        return client.post(
            "/api/user/signup",
            json=user_create.model_dump(mode="json"),
        )

    def _test_fail_ret_res(response: TestResponse):
        res = ResponseModel.model_validate(response.json)
        assert res.status == "ERROR"
        assert res.error is not None
        return res

    def _validation_test_fail(usr: User):
        response = _send_request(usr, "asd")
        res = _test_fail_ret_res(response)
        assert isinstance(res.error, BadRequest)

    response = client.post(
        "/api/user/signup",
        json={
            "random": "data",
        },
    )
    res = _test_fail_ret_res(response)

    # length checks
    TEST_USER.username = "012345678901234567890"
    TEST_USER.first_name = "abcdefghijklmnopqrstu"
    _validation_test_fail(TEST_USER)

    TEST_USER.username = "012_"
    TEST_USER.first_name = "A"
    _validation_test_fail(TEST_USER)

    # character checks
    TEST_USER.username = "0123456789-"
    TEST_USER.first_name = "Ac"
    _validation_test_fail(TEST_USER)

    TEST_USER.username = "0123_"
    TEST_USER.first_name = "ABc1"
    _validation_test_fail(TEST_USER)

    TEST_USER.username = "!@#$%^&*()_+{}:?<>"
    TEST_USER.first_name = "!@#$%^&*()_+{}:?<>"
    _validation_test_fail(TEST_USER)

    TEST_USER.username = "0123456789012345678_"
    TEST_USER.first_name = "abcdefghijklmnopqrst"
    response = _send_request(TEST_USER, "asd")
    res = _test_fail_ret_res(response)
    assert isinstance(res.error, PreRegistrationNotFound)

    key, preuser = create_precreated_user(TEST_USER.email)
    assert preuser is not None
    response = _send_request(TEST_USER, "asd")
    res = _test_fail_ret_res(response)
    assert isinstance(res.error, InvalidLicenseKey)

    response = _send_request(TEST_USER, key)
    assert response.status_code == 201
    res = UserResponseModel.model_validate(response.json)
    assert res.status == "OK"
    assert res.data is not None
    TEST_USER.id = res.data.id
    user_read = UserRead.model_validate(TEST_USER.model_dump())
    assert user_read.last_login.timestamp() <= res.data.last_login.timestamp()
    user_read.last_login = res.data.last_login
    assert res.data == user_read

    TEST_USER.email = "test@test.test"
    key, preuser = create_precreated_user(TEST_USER.email)
    response = _send_request(TEST_USER, key)
    res = _test_fail_ret_res(response)
    assert isinstance(res.error, UsernameTaken)


def test_login(client: FlaskClient):
    TEST_USER = random_user()
    key, _ = create_precreated_user(TEST_USER.email)
    response = client.post(
        "/api/user/signup",
        json=UserCreate.model_validate(
            {
                **TEST_USER.model_dump(),
                "license_key": key,
                "password": TEST_USER.password_hash,
            }
        ).model_dump(),
    )
    res = UserResponseModel.model_validate(response.json)
    assert res.status == "OK"

    response = client.post(
        "/api/user/login",
        json={
            "username": TEST_USER.username,
            "password": TEST_USER.password_hash,
        },
    )
    assert response.status_code == 200
    res = UserResponseModel.model_validate(response.json)
    assert res.status == "OK"
    assert res.data is not None
    TEST_USER.id = res.data.id
    user_read = UserRead.model_validate(TEST_USER.model_dump())
    assert user_read.last_login.timestamp() <= res.data.last_login.timestamp()
    user_read.last_login = res.data.last_login
    assert res.data == user_read

    response = client.post(
        "/api/user/login",
        json={
            "username": "AAAAAA",
            "password": TEST_USER.password_hash,
        },
    )

    assert response.status_code == InvalidCredentials.status_code
    res = UserResponseModel.model_validate(response.json)
    assert res.status == "ERROR"
    assert isinstance(res.error, InvalidCredentials)
    assert res.data is None

    response = client.post(
        "/api/user/login",
        json={
            "username": TEST_USER.username,
            "password": "wrong_password",
        },
    )
    assert response.status_code == InvalidCredentials.status_code
    res = UserResponseModel.model_validate(response.json)
    assert res.status == "ERROR"
    assert isinstance(res.error, InvalidCredentials)
    assert res.data is None


def test_sessions(client: FlaskClient):
    def _test_session(user: User | None):
        with client.session_transaction() as session:
            if user is None:
                assert session.get("username") is None
            else:
                assert session.get("username") == user.username
        response = client.get("/api/user/me")
        if user is None:
            assert response.status_code == InvalidCredentials.status_code
        else:
            assert response.status_code == 200
        res = UserResponseModel.model_validate(response.json)
        if user is None:
            assert res.status == "ERROR"
            assert isinstance(res.error, Unauthorized)
        else:
            assert res.status == "OK"
            assert res.data is not None
            user_read = UserRead.model_validate(user.model_dump())
            assert res.data == user_read
            assert res.data.last_login.timestamp() != 0

    _test_session(None)

    def _test_user_creation(user: User):
        key, _ = create_precreated_user(user.email)
        res = UserResponseModel.model_validate(
            client.post(
                "/api/user/signup",
                json=UserCreate.model_validate(
                    {
                        **user.model_dump(),
                        "license_key": key,
                        "password": user.password_hash,
                    }
                ).model_dump(),
            ).json
        )
        assert res.status == "OK"
        assert res.data is not None
        user.id = res.data.id
        user.last_login = res.data.last_login
        _test_session(user)
        return user

    user1 = _test_user_creation(random_user())
    user2 = _test_user_creation(random_user())

    response = client.post("/api/user/logout")
    assert response.status_code == 200
    _test_session(None)

    def _login(uname: str, pwd: str, user: User):
        res = UserResponseModel.model_validate(
            client.post(
                "/api/user/login",
                json=UserLoginRequestModel.model_validate(
                    {
                        "username": uname,
                        "password": pwd,
                    }
                ).model_dump(),
            ).json
        )
        if res.data:
            assert user.last_login.timestamp() <= res.data.last_login.timestamp()
            user.last_login = res.data.last_login
        return user

    user1 = _login(user1.username, user1.password_hash, user1)
    _test_session(user1)
    user2 = _login(user2.username, user2.password_hash, user2)
    _test_session(user2)
    _login(user1.username, user2.password_hash, user1)
    _test_session(user2)
    response = client.post("/api/user/logout")
    assert response.status_code == 200
    _test_session(None)
    _login(user2.username, user1.password_hash, user1)
    _test_session(None)


def test_forgot_verify_reset_password(
    monkeypatch: MonkeyPatch, client: FlaskClient, get_db: GetDatabase
):
    curr_user: User | None = None
    curr_token: str | None = None

    def mock_send_reset_password_token(user: User, token: str):
        nonlocal curr_user, curr_token
        curr_user = user
        curr_token = token

    monkeypatch.setattr(
        "flaskr.api.email_service.send_reset_password_token",
        mock_send_reset_password_token,
    )

    userdb = get_db().users
    tokendb = get_db().tokens
    TEST_USER = random_user()

    TEST_USER.id = userdb.insert_one(
        TEST_USER.model_dump(exclude_none=True)
    ).inserted_id

    assert (
        client.post(
            "/api/user/forgot-password",
            json=UserForgotPasswordModel(email="fakeemail").model_dump(),
        ).status_code
        == 200
    )
    assert curr_user is None
    assert (
        client.post(
            "/api/user/forgot-password",
            json=UserForgotPasswordModel(email=TEST_USER.email).model_dump(),
        ).status_code
        == 200
    )
    assert tokendb.count_documents({}) == 1
    assert curr_user is not None
    assert curr_user == TEST_USER

    response = client.post(
        "/api/user/verify-token",
        json=UserVerifyTokenModel(
            username=TEST_USER.username, token="fake_token"
        ).model_dump(),
    )
    assert response.status_code == InvalidResetToken.status_code
    res = ResponseModel.model_validate(response.json)
    assert res.status == "ERROR"
    assert isinstance(res.error, InvalidResetToken)

    response = client.post(
        "/api/user/verify-token",
        json=UserVerifyTokenModel(
            username=TEST_USER.username, token=curr_token
        ).model_dump(),
    )
    assert response.status_code == 200
    res = ResponseModel.model_validate(response.json)
    assert res.status == "OK"

    prev_token = curr_token
    curr_token = None
    assert (
        client.post(
            "/api/user/forgot-password",
            json=UserForgotPasswordModel(email=TEST_USER.email).model_dump(),
        ).status_code
        == 200
    )
    assert tokendb.count_documents({}) == 1
    assert curr_user is not None
    assert curr_user == TEST_USER
    assert curr_token != prev_token

    response = client.post(
        "/api/user/verify-token",
        json=UserVerifyTokenModel(
            username=TEST_USER.username, token=prev_token
        ).model_dump(),
    )
    assert response.status_code == InvalidResetToken.status_code
    res = ResponseModel.model_validate(response.json)
    assert res.status == "ERROR"
    assert isinstance(res.error, InvalidResetToken)

    response = client.post(
        "/api/user/verify-token",
        json=UserVerifyTokenModel(
            username="wrong_username", token=curr_token
        ).model_dump(),
    )
    assert response.status_code == InvalidResetToken.status_code
    res = ResponseModel.model_validate(response.json)
    assert res.status == "ERROR"
    assert isinstance(res.error, InvalidResetToken)

    response = client.post(
        "/api/user/verify-token",
        json=UserVerifyTokenModel(
            username="wrong_username", token="wrong_token"
        ).model_dump(),
    )
    assert response.status_code == InvalidResetToken.status_code
    res = ResponseModel.model_validate(response.json)
    assert res.status == "ERROR"
    assert isinstance(res.error, InvalidResetToken)

    # assume reset password invalid token handling the exact same as verify
    response = client.put(
        "/api/user/reset-password",
        json=UserResetPasswordModel(
            username=TEST_USER.username, token=curr_token, password="new_password"
        ).model_dump(),
    )
    assert response.status_code == 200
    res = ResponseModel.model_validate(response.json)
    assert res.status == "OK"

    response = client.post(
        "/api/user/login",
        json=UserLoginRequestModel.model_validate(
            {
                "username": TEST_USER.username,
                "password": "new_password",
            }
        ).model_dump(),
    )
    assert response.status_code == 200
    res = UserResponseModel.model_validate(response.json)
    assert res.status == "OK"
    assert res.data.last_login >= TEST_USER.last_login
    TEST_USER.last_login = res.data.last_login
    assert res.data == UserRead.model_validate(TEST_USER.model_dump())
