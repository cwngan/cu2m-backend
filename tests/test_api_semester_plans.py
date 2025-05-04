from datetime import datetime
from typing import Any

import pytest
from flask.testing import FlaskClient

from flaskr.api.APIExceptions import (
    BadRequest,
    DuplicateResource,
    NotFound,
    Unauthorized,
)
from flaskr.api.respmodels import ResponseModel, SemesterPlanResponseModel
from flaskr.db.models import CoursePlan, SemesterPlanCreate, SemesterPlanRead, User
from tests.utils import GetDatabase, random_string, random_user

JSON = dict[str, Any]


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
def test_course_plan(test_user: User, get_db: GetDatabase):
    assert test_user.id is not None
    course_plan = CoursePlan(
        description=random_string(20),
        name=random_string(),
        user_id=test_user.id,
        favourite=False,
        updated_at=datetime.now(),
    )
    course_plan_id = (
        get_db()
        .course_plans.insert_one(course_plan.model_dump(exclude_none=True))
        .inserted_id
    )
    course_plan.id = course_plan_id
    return course_plan


@pytest.fixture
def test_course_plan_2(test_user_2: User, get_db: GetDatabase):
    assert test_user_2.id is not None
    course_plan = CoursePlan(
        description=random_string(20),
        name=random_string(),
        user_id=test_user_2.id,
        favourite=False,
        updated_at=datetime.now(),
    )
    course_plan_id = (
        get_db()
        .course_plans.insert_one(course_plan.model_dump(exclude_none=True))
        .inserted_id
    )
    course_plan.id = course_plan_id
    return course_plan


@pytest.fixture
def logged_in_client(test_user: User, client: FlaskClient):
    with client.session_transaction() as session:
        session["username"] = test_user.username
    yield client


@pytest.fixture
def logged_in_client_2(test_user_2: User, client_2: FlaskClient):
    with client_2.session_transaction() as session:
        session["username"] = test_user_2.username
    yield client_2


@pytest.mark.parametrize(
    "method, endpoint",
    [
        ("GET", "id"),
        ("POST", ""),
        ("PATCH", "id"),
        ("DELETE", "id"),
    ],
)
def test_unauthenticated_access(client: FlaskClient, method: str, endpoint: str):
    base_url = "/api/semester-plans/"
    response = client.open(f"{base_url}{endpoint}", method=method)
    assert response.status_code == Unauthorized.status_code
    course_plan_response = ResponseModel.model_validate(response.json)
    assert course_plan_response.status == "ERROR"
    assert isinstance(course_plan_response.error, Unauthorized)


def test_create_semester_plan(
    logged_in_client: FlaskClient, test_course_plan: CoursePlan
):
    assert test_course_plan.id is not None
    semester_plan_data = SemesterPlanCreate(
        course_plan_id=test_course_plan.id,
        semester=1,
        year=2025,
    )
    response = logged_in_client.post(
        "/api/semester-plans/", json=semester_plan_data.model_dump(mode="json")
    )
    assert response.status_code == 200
    data = SemesterPlanResponseModel.model_validate(response.get_json())
    assert data.status == "OK"
    assert data.data is not None
    assert data.data.course_plan_id == semester_plan_data.course_plan_id
    assert data.data.semester == semester_plan_data.semester
    assert data.data.year == semester_plan_data.year


def test_get_semester_plan(logged_in_client: FlaskClient, test_course_plan: CoursePlan):
    assert test_course_plan.id is not None
    semester_plan_data = SemesterPlanCreate(
        course_plan_id=test_course_plan.id,
        semester=1,
        year=2025,
    )
    create_response = logged_in_client.post(
        "/api/semester-plans/", json=semester_plan_data.model_dump(mode="json")
    )
    assert create_response.status_code == 200
    created_data = create_response.get_json()["data"]

    response = logged_in_client.get(f"/api/semester-plans/{created_data['_id']}")
    assert response.status_code == 200
    data = SemesterPlanResponseModel.model_validate(response.get_json())
    assert data.status == "OK"
    assert data.data is not None
    assert data.data.course_plan_id == semester_plan_data.course_plan_id
    assert data.data.semester == semester_plan_data.semester
    assert data.data.year == semester_plan_data.year


def test_update_semester_plan(
    logged_in_client: FlaskClient, test_course_plan: CoursePlan
):
    assert test_course_plan.id is not None
    semester_plan_data = SemesterPlanCreate(
        course_plan_id=test_course_plan.id,
        semester=1,
        year=2025,
    )
    create_response = logged_in_client.post(
        "/api/semester-plans/", json=semester_plan_data.model_dump(mode="json")
    )
    assert create_response.status_code == 200
    created_data = create_response.get_json()["data"]

    updated_data: JSON = {
        "courses": ["ENGG1110", "CSCI1130"],
        "semester": 2,
        "year": 2026,
    }
    response = logged_in_client.patch(
        f"/api/semester-plans/{created_data['_id']}", json=updated_data
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "OK"
    assert data["data"]["semester"] == updated_data["semester"]
    assert data["data"]["year"] == updated_data["year"]
    assert data["data"]["courses"] == ["ENGG1110", "CSCI1130"]


def test_delete_semester_plan(
    logged_in_client: FlaskClient, test_course_plan: CoursePlan
):
    assert test_course_plan.id is not None
    semester_plan_data = SemesterPlanCreate(
        course_plan_id=test_course_plan.id,
        semester=1,
        year=2025,
    )
    create_response = logged_in_client.post(
        "/api/semester-plans/", json=semester_plan_data.model_dump(mode="json")
    )
    assert create_response.status_code == 200
    created_data = create_response.get_json()["data"]

    response = logged_in_client.delete(f"/api/semester-plans/{created_data['_id']}")
    assert response.status_code == 200
    assert response.get_json()["status"] == "OK"

    # Try to delete the same thing to ensure the system is working properly
    response = logged_in_client.delete(f"/api/semester-plans/{created_data['_id']}")
    assert response.status_code == NotFound.status_code
    res = ResponseModel.model_validate(response.json)
    assert res.status == "ERROR"
    assert isinstance(res.error, NotFound)


def test_semester_plan_uniqueness(
    logged_in_client: FlaskClient, test_course_plan: CoursePlan
):
    assert test_course_plan.id is not None
    semester_plan_data = SemesterPlanCreate(
        course_plan_id=test_course_plan.id,
        semester=1,
        year=2025,
    )
    create_response = logged_in_client.post(
        "/api/semester-plans/", json=semester_plan_data.model_dump(mode="json")
    )
    assert create_response.status_code == 200

    # Create a semester plan with same semester and year, should return with error
    create_response = logged_in_client.post(
        "/api/semester-plans/", json=semester_plan_data.model_dump(mode="json")
    )
    assert create_response.status_code == DuplicateResource.status_code
    res = SemesterPlanResponseModel.model_validate(create_response.json)
    assert isinstance(res.error, DuplicateResource)


def test_creating_all_valid_semesters(
    logged_in_client: FlaskClient, test_course_plan: CoursePlan
):
    assert test_course_plan.id is not None
    for num in range(1, 4):
        semester_plan_data = SemesterPlanCreate(
            course_plan_id=test_course_plan.id,
            semester=num,
            year=2025,
        )
        create_response = logged_in_client.post(
            "/api/semester-plans/", json=semester_plan_data.model_dump(mode="json")
        )
        assert create_response.status_code == 200


def test_creating_invalid_semesters(
    logged_in_client: FlaskClient, test_course_plan: CoursePlan
):
    assert test_course_plan.id is not None
    for num in [0, 4, -100, 69420]:
        semester_plan_data: JSON = {
            "course_plan_id": str(test_course_plan.id),
            "semester": num,
            "year": 2025,
        }
        create_response = logged_in_client.post(
            "/api/semester-plans/", json=semester_plan_data
        )
        assert create_response.status_code == BadRequest.status_code
        res = SemesterPlanResponseModel.model_validate(create_response.json)
        assert res.status == "ERROR"
        assert isinstance(res.error, BadRequest)


def test_update_invalid_semester_number(
    logged_in_client: FlaskClient, test_course_plan: CoursePlan
):
    assert test_course_plan.id is not None
    semester_plan_data = SemesterPlanCreate(
        course_plan_id=test_course_plan.id,
        semester=1,
        year=2025,
    )
    create_response = logged_in_client.post(
        "/api/semester-plans/", json=semester_plan_data.model_dump(mode="json")
    )
    assert create_response.status_code == 200
    created_data = create_response.get_json()["data"]

    for num in [0, 4, -100, 69420]:
        updated_data = {
            "semester": num,
            "year": 2026,
        }
        response = logged_in_client.patch(
            f"/api/semester-plans/{created_data['_id']}", json=updated_data
        )
        assert response.status_code == BadRequest.status_code
        res = SemesterPlanResponseModel.model_validate(response.json)
        assert res.status == "ERROR"
        assert isinstance(res.error, BadRequest)


def test_different_user_access_same_semester_plan(
    logged_in_client: FlaskClient,
    logged_in_client_2: FlaskClient,
    test_course_plan: CoursePlan,
    test_course_plan_2: CoursePlan,
):
    assert test_course_plan.id is not None
    assert test_course_plan_2.id is not None
    semester_plan = SemesterPlanCreate(
        course_plan_id=test_course_plan.id,
        semester=1,
        year=2025,
    )
    semester_plan_2 = SemesterPlanCreate(
        course_plan_id=test_course_plan_2.id,
        semester=1,
        year=2025,
    )

    # Malicious post request
    response = logged_in_client.post(
        "/api/semester-plans/", json=semester_plan_2.model_dump(mode="json")
    )
    response_2 = logged_in_client_2.post(
        "/api/semester-plans/", json=semester_plan.model_dump(mode="json")
    )
    assert (
        response.status_code == NotFound.status_code
        and response_2.status_code == NotFound.status_code
    )
    res = SemesterPlanResponseModel.model_validate(response.json)
    res_2 = SemesterPlanResponseModel.model_validate(response_2.json)
    assert res.status == "ERROR" and res_2.status == "ERROR"
    assert isinstance(res.error, NotFound) and isinstance(res_2.error, NotFound)

    # Normal creation for later tests
    response = logged_in_client.post(
        "/api/semester-plans/", json=semester_plan.model_dump(mode="json")
    )
    response_2 = logged_in_client_2.post(
        "/api/semester-plans/", json=semester_plan_2.model_dump(mode="json")
    )
    # Sanity check
    assert response.status_code == 200 and response_2.status_code == 200
    assert response.get_json()["status"] == response_2.get_json()["status"] == "OK"

    # Update semester plan
    semester_plan = SemesterPlanResponseModel.model_validate(response.get_json()).data
    semester_plan_2 = SemesterPlanResponseModel.model_validate(
        response_2.get_json()
    ).data

    assert semester_plan is not None and semester_plan_2 is not None

    def _cross_access(malicious_client: FlaskClient, innocent_plan: SemesterPlanRead):
        get_response = malicious_client.get(f"/api/semester-plans/{innocent_plan.id}")
        patch_response = malicious_client.patch(
            f"/api/semester-plans/{innocent_plan.id}", json={"semester": 2}
        )
        delete_response = malicious_client.delete(
            f"/api/semester-plans/{innocent_plan.id}"
        )
        responses = [get_response, patch_response, delete_response]
        for response in responses:
            assert response.status_code == NotFound.status_code
            res = SemesterPlanResponseModel.model_validate(response.json)
            assert res.status == "ERROR"
            assert isinstance(res.error, NotFound)

    # User 2 access user 1 semester plan should get error
    _cross_access(logged_in_client_2, semester_plan)
    # User 1 access user 2 semester plan should get error
    _cross_access(logged_in_client, semester_plan_2)
