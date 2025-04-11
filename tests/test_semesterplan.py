import pytest
from flask.testing import FlaskClient


@pytest.fixture
def semester_plan_data():
    return {
        "course_plan_id": "12345",
        "semester": 1,
        "year": 2025,
    }


def test_create_semester_plan(client: FlaskClient, semester_plan_data):
    response = client.post("/semester_plans/", json=semester_plan_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "SUCCESS"
    assert data["data"]["course_plan_id"] == semester_plan_data["course_plan_id"]
    assert data["data"]["semester"] == semester_plan_data["semester"]
    assert data["data"]["year"] == semester_plan_data["year"]


def test_read_semester_plan(client: FlaskClient, semester_plan_data):
    # First, create a semester plan
    create_response = client.post("/semester_plans/", json=semester_plan_data)
    assert create_response.status_code == 200
    created_data = create_response.get_json()["data"]

    # Now, read the semester plan
    response = client.get(f"/semester_plans/?id={created_data['_id']}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "SUCCESS"
    assert data["data"]["course_plan_id"] == semester_plan_data["course_plan_id"]
    assert data["data"]["semester"] == semester_plan_data["semester"]
    assert data["data"]["year"] == semester_plan_data["year"]


def test_update_semester_plan(client: FlaskClient, semester_plan_data):
    # First, create a semester plan
    create_response = client.post("/semester_plans/", json=semester_plan_data)
    assert create_response.status_code == 200
    created_data = create_response.get_json()["data"]

    # Update the semester plan
    updated_data = {"semester": 2, "year": 2026}
    response = client.put(
        f"/semester_plans/?id={created_data['_id']}", json=updated_data
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "SUCCESS"
    assert data["data"]["semester"] == updated_data["semester"]
    assert data["data"]["year"] == updated_data["year"]


def test_delete_semester_plan(client: FlaskClient, semester_plan_data):
    # First, create a semester plan
    create_response = client.post("/semester_plans/", json=semester_plan_data)
    assert create_response.status_code == 200
    created_data = create_response.get_json()["data"]

    # Delete the semester plan
    response = client.delete(f"/semester_plans/?id={created_data['_id']}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "SUCCESS"
