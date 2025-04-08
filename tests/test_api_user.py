import json
from datetime import datetime

from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from flaskr.api.respmodels import ResponseModel, UserResponseModel
from flaskr.db.models import User, UserCreate, UserRead
from flaskr.db.user import create_precreated_user
from tests.utils import random_user


def test_signup(client: FlaskClient):
    TEST_USER = random_user()

    def _send_request(usr: User, key: str):
        user_create = UserCreate.model_validate(
            {
                **usr.model_dump(),
                "license_key": key,
                "password": usr.password_hash,
            }
        )

        return client.post(
            "/api/user/signup",
            json=user_create.model_dump(),
        )

    def _test_fail_ret_res(response: TestResponse):
        assert response.status_code == 400
        res = ResponseModel.model_validate(response.json)
        assert res.status == "ERROR"
        assert res.error is not None
        return res

    def _validation_test_fail(usr: User, s: set[str]):
        response = _send_request(usr, "asd")
        res = _test_fail_ret_res(response)
        assert res.error is not None
        json_data = json.loads(res.error)
        assert s == set(e["loc"][0] for e in json_data)

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
    _validation_test_fail(TEST_USER, {"username", "first_name"})

    TEST_USER.username = "012_"
    TEST_USER.first_name = "A"
    _validation_test_fail(TEST_USER, {"username", "first_name"})

    # character checks
    TEST_USER.username = "0123456789-"
    TEST_USER.first_name = "Ac"
    _validation_test_fail(TEST_USER, {"username"})

    TEST_USER.username = "0123_"
    TEST_USER.first_name = "ABc1"
    _validation_test_fail(TEST_USER, {"first_name"})

    TEST_USER.username = "!@#$%^&*()_+{}:?<>"
    TEST_USER.first_name = "!@#$%^&*()_+{}:?<>"
    _validation_test_fail(TEST_USER, {"username", "first_name"})

    TEST_USER.username = "0123456789012345678_"
    TEST_USER.first_name = "abcdefghijklmnopqrst"
    response = _send_request(TEST_USER, "asd")
    res = _test_fail_ret_res(response)
    assert res.error == "Pre-registration not found."

    key, preuser = create_precreated_user(TEST_USER.email)
    assert preuser is not None
    response = _send_request(TEST_USER, "asd")
    res = _test_fail_ret_res(response)
    assert res.error == "Invalid license key."

    response = _send_request(TEST_USER, key)
    assert response.status_code == 201
    res = UserResponseModel.model_validate(response.json)
    assert res.status == "OK"
    user_read = UserRead.model_validate(res.data)
    TEST_USER.id = user_read.id
    test_user_read = UserRead.model_validate(TEST_USER.model_dump())
    test_user_read.last_login = user_read.last_login
    assert user_read == test_user_read
    assert user_read.last_login != datetime.fromtimestamp(0)

    TEST_USER.email = "test@test.test"
    key, preuser = create_precreated_user(TEST_USER.email)
    response = _send_request(TEST_USER, key)
    res = _test_fail_ret_res(response)
    assert res.error == "Username already taken."

    # test for sessions?


def test_login(client: FlaskClient):
    TEST_USER = random_user()
    TEST_USER.first_name = "AA"
    TEST_USER.username = "AAAAA"
    key, preuser = create_precreated_user(TEST_USER.email)
    assert preuser is not None
    TEST_USER.license_key_hash = key
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
    user_read = UserRead.model_validate(res.data)
    TEST_USER.id = user_read.id
    test_user_read = UserRead.model_validate(TEST_USER.model_dump())
    test_user_read.last_login = user_read.last_login
    assert user_read == test_user_read
    assert user_read.last_login != datetime.fromtimestamp(0)

    response = client.post(
        "/api/user/login",
        json={
            "username": "AAAAAA",
            "password": TEST_USER.password_hash,
        },
    )

    assert response.status_code == 401
    res = UserResponseModel.model_validate(response.json)
    assert res.status == "ERROR"
    assert res.error == "Invalid username or password."
    assert res.data is None

    response = client.post(
        "/api/user/login",
        json={
            "username": TEST_USER.username,
            "password": "wrong_password",
        },
    )
    assert response.status_code == 401
    res = UserResponseModel.model_validate(response.json)
    assert res.status == "ERROR"
    assert res.error == "Invalid username or password."
    assert res.data is None
    # test for sessions?
