import pytest
from flask.testing import FlaskClient

from tests.utils import random_user, random_string, GetDatabase
from datetime import datetime


@pytest.fixture
def test_user(get_db: GetDatabase):
    user = random_user()
    user.id = get_db().users.insert_one(user.model_dump(exclude_none=True)).inserted_id
    return user


@pytest.fixture
def test_courseplan(test_user, get_db: GetDatabase):
    course_plan = {
        "description": random_string(20),
        "name": random_string(),
        "user_id": test_user.id,
        "favourite": False,  # Added field
        "updated_at": datetime.now(),  # Added field
    }
    course_plan_id = get_db().course_plans.insert_one(course_plan).inserted_id
    course_plan["_id"] = course_plan_id
    return course_plan


@pytest.fixture
def logged_in_client(test_user, client: FlaskClient):
    with client.session_transaction() as session:
        session["username"] = test_user.username
    yield client


def test_create_semester_plan(logged_in_client, test_courseplan):
    semester_plan_data = {
        "course_plan_id": str(test_courseplan["_id"]),
        "semester": 1,
        "year": 2025,
    }
    response = logged_in_client.post("/api/semester_plans/", json=semester_plan_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "OK"
    assert data["data"]["course_plan_id"] == semester_plan_data["course_plan_id"]
    assert data["data"]["semester"] == semester_plan_data["semester"]
    assert data["data"]["year"] == semester_plan_data["year"]


def test_get_semester_plan(logged_in_client, test_courseplan):
    semester_plan_data = {
        "course_plan_id": str(test_courseplan["_id"]),
        "semester": 1,
        "year": 2025,
    }
    create_response = logged_in_client.post(
        "/api/semester_plans/", json=semester_plan_data
    )
    assert create_response.status_code == 200
    created_data = create_response.get_json()["data"]

    response = logged_in_client.get(f"/api/semester_plans/{created_data['_id']}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "OK"
    assert data["data"]["course_plan_id"] == semester_plan_data["course_plan_id"]
    assert data["data"]["semester"] == semester_plan_data["semester"]
    assert data["data"]["year"] == semester_plan_data["year"]


def test_update_semester_plan(logged_in_client, test_courseplan):
    semester_plan_data = {
        "course_plan_id": str(test_courseplan["_id"]),
        "semester": 1,
        "year": 2025,
    }
    create_response = logged_in_client.post(
        "/api/semester_plans/", json=semester_plan_data
    )
    assert create_response.status_code == 200
    created_data = create_response.get_json()["data"]

    updated_data = {
        "semester": 2,
        "year": 2026,
    }
    response = logged_in_client.put(
        f"/api/semester_plans/{created_data['_id']}", json=updated_data
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "OK"
    assert data["data"]["semester"] == updated_data["semester"]
    assert data["data"]["year"] == updated_data["year"]


def test_delete_semester_plan(logged_in_client, test_courseplan):
    semester_plan_data = {
        "course_plan_id": str(test_courseplan["_id"]),
        "semester": 1,
        "year": 2025,
    }
    create_response = logged_in_client.post(
        "/api/semester_plans/", json=semester_plan_data
    )
    assert create_response.status_code == 200
    created_data = create_response.get_json()["data"]

    response = logged_in_client.delete(f"/api/semester_plans/{created_data['_id']}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "OK"
