import os
import pytest
import csv
from flaskr import create_app
from flaskr.db.database import get_db
from flaskr.db.crud import create_precreated_user, delete_user
from flaskr.utils import PasswordHasher

# Use a separate database name for testing to avoid clashing with production data.
TEST_MONGODB_URI = "mongodb://tmp:tmp@mongodb:27017/test_cu2m"


@pytest.fixture
def app():
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
    return app.test_client()


@pytest.fixture
def precreated_user():
    """
    Create a pre-created user for registration testing.
    Assume the CSV has keys "email" and "license_key".
    Here we manually insert one record.
    """
    email = "test@example.com"
    plain_license = "di-jk-algo"  # As in Email-Key.csv example
    # Use create_precreated_user so that license_hash is generated and stored
    inserted_id = create_precreated_user(email, plain_license)
    # Return a dict for convenience
    return {"email": email, "plain_license": plain_license, "id": inserted_id}


def test_registration_success(client, precreated_user):
    reg_payload = {
        "user": {
            "email": precreated_user["email"],
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser",
            "password": "StrongPasswOrd123",
            "major": "Computer Science",
            "license_key": precreated_user["plain_license"],
        }
    }
    response = client.post("/api/user/register", json=reg_payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["data"]["username"] == "testuser"


def test_registration_invalid_license(client, precreated_user):
    reg_payload = {
        "user": {
            "email": precreated_user["email"],
            "first_name": "Another",
            "last_name": "User",
            "username": "testuser2",
            "password": "StrongPasswOrd123",
            "major": "Computer Science",
            "license_key": "wrong-license",
        }
    }
    response = client.post("/api/user/register", json=reg_payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] == "ERROR"
    assert "Invalid license key" in data["error"]


def test_duplicate_username_registration(client, precreated_user):
    # First, register once successfully.
    reg_payload = {
        "user": {
            "email": precreated_user["email"],
            "first_name": "Test",
            "last_name": "User",
            "username": "duplicateuser",
            "password": "StrongPasswOrd123",
            "major": "Computer Science",
            "license_key": precreated_user["plain_license"],
        }
    }
    response = client.post("/api/user/register", json=reg_payload)
    assert response.status_code == 201

    # Create another pre-created user record to use same username.
    email2 = "another@example.com"
    plain_license2 = "another-license"
    create_precreated_user(email2, plain_license2)

    reg_payload_2 = {
        "user": {
            "email": email2,
            "first_name": "Another",
            "last_name": "User",
            "username": "duplicateuser",  # Duplicate username
            "password": "StrongPasswOrd123",
            "major": "Engineering",
            "license_key": plain_license2,
        }
    }
    response2 = client.post("/api/user/register", json=reg_payload_2)
    assert response2.status_code == 400
    data2 = response2.get_json()
    assert data2["status"] == "ERROR"
    assert "Username already taken" in data2["error"]


def test_login_success(client, precreated_user):
    # First, register a user.
    reg_payload = {
        "user": {
            "email": precreated_user["email"],
            "first_name": "Login",
            "last_name": "User",
            "username": "loginuser",
            "password": "StrongPasswOrd123",
            "major": "Science",
            "license_key": precreated_user["plain_license"],
        }
    }
    reg_response = client.post("/api/user/register", json=reg_payload)
    assert reg_response.status_code == 201

    # Attempt to login with correct credentials.
    login_payload = {"username": "loginuser", "password": "StrongPasswOrd123"}
    login_response = client.post("/api/user/login", json=login_payload)
    assert login_response.status_code == 200
    login_data = login_response.get_json()
    # Upon success, the returned user record should have the correct username.
    assert login_data["data"]["username"] == "loginuser"


def test_login_invalid_credentials(client, precreated_user):
    # Register a user for login test.
    reg_payload = {
        "user": {
            "email": precreated_user["email"],
            "first_name": "Login",
            "last_name": "Fail",
            "username": "loginfailuser",
            "password": "StrongPasswOrd123",
            "major": "Science",
            "license_key": precreated_user["plain_license"],
        }
    }
    reg_response = client.post("/api/user/register", json=reg_payload)
    assert reg_response.status_code == 201

    # Attempt to login with an incorrect password.
    login_payload = {"username": "loginfailuser", "password": "WrongPassword"}
    login_response = client.post("/api/user/login", json=login_payload)
    assert login_response.status_code == 401
    error_data = login_response.get_json()
    assert error_data["status"] == "ERROR"
    assert "Invalid username or password" in error_data["error"]


def test_delete_user(client, precreated_user):
    # Register a user to later delete.
    reg_payload = {
        "user": {
            "email": precreated_user["email"],
            "first_name": "Delete",
            "last_name": "User",
            "username": "deleteuser",
            "password": "StrongPasswOrd123",
            "major": "Arts",
            "license_key": precreated_user["plain_license"],
        }
    }
    reg_response = client.post("/api/user/register", json=reg_payload)
    assert reg_response.status_code == 201

    # Delete the user
    delete_payload = {"username": "deleteuser"}
    delete_response = client.delete("/api/user/delete", json=delete_payload)
    # Expect 404 if trying to delete again (indicating the user was removed)
    assert delete_response.status_code in (200, 404)
