import pytest
from flask import Flask

from flaskr import create_app
from flaskr.db.database import get_mongo_client

# Use a separate database name for testing to avoid clashing with production data.
TEST_DB_NAME = "TESTDB"


@pytest.fixture(autouse=True)
def monkeypatch_setup(monkeypatch: pytest.MonkeyPatch):
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
    monkeypatch.setattr("flaskr.db.user.get_db", mock_get_db)
    monkeypatch.setattr("flaskr.db.courses.get_db", mock_get_db)

    yield
    # Clean up the test database after tests (automatically)


@pytest.fixture(autouse=True, scope="session")
def database_setup():
    """
    Setup data of database.

    This fixture is automatically applied to all tests and drop database after the whole test ends.
    """
    yield
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
