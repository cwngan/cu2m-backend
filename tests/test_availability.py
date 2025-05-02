import re
from datetime import datetime

from conftest import TEST_DB_NAME
from flask.testing import FlaskClient

from flaskr.api.errors import ResponseError
from flaskr.api.respmodels import ResponseModel
from flaskr.db.user import create_precreated_user, get_precreated_user
from tests.utils import GetDatabase


def test_api_root(client: FlaskClient):
    """
    Tests if the Flask app API root endpoint is reachable.
    """
    response = client.get("/api/")
    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data.get("status") == "OK"
    assert data.get("data") == "CU^2M API"


def test_api_ping(client: FlaskClient):
    """
    Tests if the Flask app ping endpoint is reachable and returns the correct response.
    """
    response = client.get("/api/ping/")
    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data.get("status") == "OK"
    assert type(data.get("data")) is str
    match_ = re.search(
        r"^Request arrived at ([0-9]{2}\-[0-9]{2}\-[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6})$",
        data.get("data"),
    )
    assert match_ is not None
    assert (
        datetime.strptime(match_.group(1), "%d-%m-%Y %H:%M:%S.%f").timestamp()
        < datetime.now().timestamp()
    )


def test_db_rw(get_db: GetDatabase):
    """
    Tests if the app is reading and writing to the correct database.
    """
    TEST_EMAIL = "test@test.test"
    db = get_db()
    assert db is not None
    assert db.name == TEST_DB_NAME

    userdb = db.users
    assert userdb is not None

    userdb.delete_many({})
    assert userdb.count_documents({}) == 0

    create_precreated_user(TEST_EMAIL)
    assert userdb.count_documents({}) == 1

    userdb.delete_many({})
    assert get_precreated_user(TEST_EMAIL) is None


def test_global_error_handler(client: FlaskClient):
    """
    Tests if the global error handler is working correctly.
    """
    response = client.get("/api/throw/")
    assert response.status_code == 500
    data = ResponseModel.model_validate(response.json)
    assert data.status == "ERROR"
    assert data.error == ResponseError.InternalError
