import re
from datetime import datetime
import pytest
from flaskr import create_app
from flaskr.db.database import get_db

# Use a separate database name for testing to avoid clashing with production data.
TEST_MONGODB_URI = "mongodb://tmp:tmp@mongodb:27017/test_cu2m"


@pytest.fixture
def app():
    """
    Create a test Flask app with a test-specific MongoDB URI.
    """
    test_config = {
        "TESTING": True,
        "MONGODB_URI": TEST_MONGODB_URI,
        "SECRET_KEY": "test-secret",
    }
    app = create_app(test_config)

    # Initialize the database (drop existing data)
    db = get_db()
    db.users.delete_many({})
    yield app
    # Clean up after tests if needed
    db.users.delete_many({})


@pytest.fixture
def client(app):
    """
    Provide a test client for the Flask app.
    """
    return app.test_client()


def test_api_root(client):
    """
    Tests if the Flask app API root endpoint is reachable.
    """
    response = client.get("/api/")
    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data.get("status") == "OK"
    assert data.get("data") == "CU^2M API"


def test_api_ping(client):
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
