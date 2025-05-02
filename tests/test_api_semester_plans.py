from datetime import datetime

import pytest
from flask.testing import FlaskClient

from flaskr.api.respmodels import ResponseModel, SemesterPlanResponseModel
from tests.utils import GetDatabase, random_string, random_user


@pytest.fixture
def test_user(get_db: GetDatabase):
    user = random_user()
    user.id = get_db().users.insert_one(user.model_dump(exclude_none=True)).inserted_id
    return user


@pytest.fixture
def test_user_2(get_db: GetDatabase):
    user = random_user()
    user.id = get_db().users.insert_one(user.model_dump(exclude_none=True)).inserted_id
    return user


@pytest.fixture
def test_course_plan(test_user, get_db: GetDatabase):
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
def test_course_plan_2(test_user_2, get_db: GetDatabase):
    course_plan = {
        "description": random_string(20),
        "name": random_string(),
        "user_id": test_user_2.id,
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


@pytest.fixture
def logged_in_client_2(test_user_2, client_2: FlaskClient):
    with client_2.session_transaction() as session:
        session["username"] = test_user_2.username
    yield client_2


@pytest.mark.parametrize(
    "method, endpoint",
    [
        ("GET", "id"),
        ("POST", ""),
        ("PUT", "id"),
        ("DELETE", "id"),
    ],
)
def test_unauthenticated_access(client: FlaskClient, method: str, endpoint: str):
    base_url = "/api/semester-plans/"
    response = client.open(f"{base_url}{endpoint}", method=method)
    assert response.status_code == 401
    course_plan_response = ResponseModel.model_validate(response.json)
    assert course_plan_response.status == "ERROR"
    assert course_plan_response.error == "Unauthorized"


def test_create_semester_plan(logged_in_client, test_course_plan):
    semester_plan_data = {
        "course_plan_id": str(test_course_plan["_id"]),
        "semester": 1,
        "year": 2025,
    }
    response = logged_in_client.post("/api/semester-plans/", json=semester_plan_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "OK"
    assert data["data"]["course_plan_id"] == semester_plan_data["course_plan_id"]
    assert data["data"]["semester"] == semester_plan_data["semester"]
    assert data["data"]["year"] == semester_plan_data["year"]


def test_get_semester_plan(logged_in_client, test_course_plan):
    semester_plan_data = {
        "course_plan_id": str(test_course_plan["_id"]),
        "semester": 1,
        "year": 2025,
    }
    create_response = logged_in_client.post(
        "/api/semester-plans/", json=semester_plan_data
    )
    assert create_response.status_code == 200
    created_data = create_response.get_json()["data"]

    response = logged_in_client.get(f"/api/semester-plans/{created_data['_id']}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "OK"
    assert data["data"]["course_plan_id"] == semester_plan_data["course_plan_id"]
    assert data["data"]["semester"] == semester_plan_data["semester"]
    assert data["data"]["year"] == semester_plan_data["year"]


def test_update_semester_plan(logged_in_client, test_course_plan):
    semester_plan_data = {
        "course_plan_id": str(test_course_plan["_id"]),
        "semester": 1,
        "year": 2025,
    }
    create_response = logged_in_client.post(
        "/api/semester-plans/", json=semester_plan_data
    )
    assert create_response.status_code == 200
    created_data = create_response.get_json()["data"]

    updated_data = {
        "semester": 2,
        "year": 2026,
    }
    response = logged_in_client.put(
        f"/api/semester-plans/{created_data['_id']}", json=updated_data
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "OK"
    assert data["data"]["semester"] == updated_data["semester"]
    assert data["data"]["year"] == updated_data["year"]


def test_delete_semester_plan(logged_in_client, test_course_plan):
    semester_plan_data = {
        "course_plan_id": str(test_course_plan["_id"]),
        "semester": 1,
        "year": 2025,
    }
    create_response = logged_in_client.post(
        "/api/semester-plans/", json=semester_plan_data
    )
    assert create_response.status_code == 200
    created_data = create_response.get_json()["data"]

    response = logged_in_client.delete(f"/api/semester-plans/{created_data['_id']}")
    assert response.status_code == 200
    assert response.get_json()["status"] == "OK"

    # Try to delete the same thing to ensure the system is working properly
    response = logged_in_client.delete(f"/api/semester-plans/{created_data['_id']}")
    assert response.status_code == 404
    assert response.get_json()["status"] == "ERROR"


def test_semester_plan_uniqueness(logged_in_client, test_course_plan):
    semester_plan_data = {
        "course_plan_id": str(test_course_plan["_id"]),
        "semester": 1,
        "year": 2025,
    }
    create_response = logged_in_client.post(
        "/api/semester-plans/", json=semester_plan_data
    )
    assert create_response.status_code == 200

    # Create a semester plan with same semester and year, should return with error
    create_response = logged_in_client.post(
        "/api/semester-plans/", json=semester_plan_data
    )
    assert create_response.status_code == 400
    assert create_response.get_json()["status"] == "ERROR"


def test_creating_all_valid_semesters(logged_in_client, test_course_plan):
    for num in range(1, 4):
        semester_plan_data = {
            "course_plan_id": str(test_course_plan["_id"]),
            "semester": num,
            "year": 2025,
        }
        create_response = logged_in_client.post(
            "/api/semester-plans/", json=semester_plan_data
        )
        assert create_response.status_code == 200


def test_creating_invalid_semesters(logged_in_client, test_course_plan):
    for num in [0, 4, -100, 69420]:
        semester_plan_data = {
            "course_plan_id": str(test_course_plan["_id"]),
            "semester": num,
            "year": 2025,
        }
        create_response = logged_in_client.post(
            "/api/semester-plans/", json=semester_plan_data
        )
        assert create_response.status_code == 400
        assert create_response.get_json()["status"] == "ERROR"


def test_update_invalid_semester_number(logged_in_client, test_course_plan):
    semester_plan_data = {
        "course_plan_id": str(test_course_plan["_id"]),
        "semester": 1,
        "year": 2025,
    }
    create_response = logged_in_client.post(
        "/api/semester-plans/", json=semester_plan_data
    )
    assert create_response.status_code == 200
    created_data = create_response.get_json()["data"]

    for num in [0, 4, -100, 69420]:
        updated_data = {
            "semester": num,
            "year": 2026,
        }
        response = logged_in_client.put(
            f"/api/semester-plans/{created_data['_id']}", json=updated_data
        )
        assert response.status_code == 400
        assert response.get_json()["status"] == "ERROR"


def test_different_user_access_same_semester_plan(
    logged_in_client, logged_in_client_2, test_course_plan, test_course_plan_2
):
    semester_plan = {
        "course_plan_id": str(test_course_plan["_id"]),
        "semester": 1,
        "year": 2025,
    }
    semester_plan_2 = {
        "course_plan_id": str(test_course_plan_2["_id"]),
        "semester": 1,
        "year": 2025,
    }

    # Malicious post request
    response = logged_in_client.post("/api/semester-plans/", json=semester_plan_2)
    response_2 = logged_in_client_2.post("/api/semester-plans/", json=semester_plan)
    assert response.status_code == 404 and response_2.status_code == 404
    assert response.get_json()["status"] == response_2.get_json()["status"] == "ERROR"

    # Normal creation for later tests
    response = logged_in_client.post("/api/semester-plans/", json=semester_plan)
    response_2 = logged_in_client_2.post("/api/semester-plans/", json=semester_plan_2)
    # Sanity check
    assert response.status_code == 200 and response_2.status_code == 200
    assert response.get_json()["status"] == response_2.get_json()["status"] == "OK"

    # Update semester plan
    semester_plan = SemesterPlanResponseModel.model_validate(response.get_json()).data
    semester_plan_2 = SemesterPlanResponseModel.model_validate(
        response_2.get_json()
    ).data

    def _cross_access(malicious_client, innocent_plan):
        get_response = malicious_client.get(f"/api/semester-plans/{innocent_plan.id}")
        put_response = malicious_client.put(
            f"/api/semester-plans/{innocent_plan.id}", json={"semester": 2}
        )
        delete_response = malicious_client.delete(
            f"/api/semester-plans/{innocent_plan.id}"
        )
        assert (
            get_response.status_code == 404
            and put_response.status_code == 404
            and delete_response.status_code == 404
        )
        assert (
            get_response.get_json()["status"] == "ERROR"
            and put_response.get_json()["status"] == "ERROR"
            and delete_response.get_json()["status"] == "ERROR"
        )

    # User 2 access user 1 semester plan should get error
    _cross_access(logged_in_client_2, semester_plan)
    # User 1 access user 2 semester plan should get error
    _cross_access(logged_in_client, semester_plan_2)
