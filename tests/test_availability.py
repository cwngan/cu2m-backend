import re
from datetime import datetime
from flaskr import create_app


def test_root():
    """
    Tests if the Flask app can be started up

    """
    app = create_app()

    with app.test_client() as client:
        response = client.get("/")
        assert response.status_code == 200
        data = response.json
        assert data is not None
        assert data.get("status") == "OK"


def test_api_root():
    """
    Tests if the Flask app API endpoint is reachable

    """
    app = create_app()

    with app.test_client() as client:
        response = client.get("/api/")
        assert response.status_code == 200
        data = response.json
        assert data is not None
        assert data.get("status") == "OK"
        assert data.get("data") == "CU^2M API"


def test_api_ping():
    """
    Tests if the Flask app is pingable

    """
    app = create_app()

    with app.test_client() as client:
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
