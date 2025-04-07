import re
from datetime import datetime

import pytest
from flask import Flask
from flask.testing import FlaskClient

from flaskr import create_app
from flaskr.db.database import get_mongo_client
from flaskr.db.user import create_precreated_user, get_precreated_user

# Use a separate database name for testing to avoid clashing with production data.
TEST_DB_NAME = "TESTDB"


@pytest.fixture(autouse=True)
def setup(monkeypatch: pytest.MonkeyPatch):
    """
    Setup testing environment.
    Monkeypatches the `get_db` function to return a test database.

    This fixture is automatically applied to all tests.
    """

    def mock_get_db():
        return get_mongo_client()[TEST_DB_NAME]

    # Note: setattr must be done to all files that imports get_db directly
    # https://stackoverflow.com/a/45466846
    monkeypatch.setattr("flaskr.db.database.get_db", mock_get_db)
    monkeypatch.setattr("flaskr.db.crud.get_db", mock_get_db)

    yield
    # Clean up the test database after tests
    get_mongo_client().drop_database(TEST_DB_NAME)


@pytest.fixture
def app():
    """
    Create a test Flask app with a test-specific MongoDB URI.
    """
    test_config = {
        "TESTING": True,
    }
    app = create_app(test_config)
    yield app


@pytest.fixture
def client(app: Flask):
    """
    Provide a test client for the Flask app.
    """
    return app.test_client()


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


def test_db_rw():
    """
    Tests if the app is reading and writing to the correct database.
    """
    from flaskr.db.database import get_db

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
