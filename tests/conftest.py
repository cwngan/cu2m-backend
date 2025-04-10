import pytest
from flask import Flask

from flaskr import create_app
from flaskr.db.database import get_mongo_client

# Use a separate database name for testing to avoid clashing with production data.
TEST_DB_NAME = "TESTDB"


@pytest.fixture(autouse=True)
def setup(monkeypatch: pytest.MonkeyPatch):
    """
    Setup testing environment.
    Monkeypatches the `get_db` function to return a test database.

    This fixture is automatically applied to all tests.
    """

    mock_used = False

    def mock_get_db():
        nonlocal mock_used
        mock_used = True
        return get_mongo_client()[TEST_DB_NAME]

    # Note: setattr must be done to all files that imports get_db directly
    # https://stackoverflow.com/a/45466846
    monkeypatch.setattr("flaskr.db.database.get_db", mock_get_db)
    monkeypatch.setattr("flaskr.db.user.get_db", mock_get_db)

    yield
    # Clean up the test database after tests
    if mock_used:
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
