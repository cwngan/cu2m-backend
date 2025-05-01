import random
from datetime import datetime, timedelta, timezone

import pytest
from flask.testing import FlaskClient

from flaskr.api.respmodels import CoursePlanResponseModel
from flaskr.db.course_plans import create_course_plan
from flaskr.db.models import CoursePlan, CoursePlanRead, CoursePlanUpdate
from tests.utils import GetDatabase, random_string, random_user


@pytest.fixture
def test_user(get_db: GetDatabase):
    """
    Insert a test user into the database before running tests.
    """
    user = random_user()
    user.id = get_db().users.insert_one(user.model_dump(exclude_none=True)).inserted_id
    return user


@pytest.fixture
def test_user2(get_db: GetDatabase):
    """
    Insert a test user into the database before running tests.
    """
    user = random_user()
    user.id = get_db().users.insert_one(user.model_dump(exclude_none=True)).inserted_id
    return user


@pytest.fixture
def course_plans(test_user) -> list[CoursePlan]:
    res = []
    for _ in range(20):
        name = random_string()
        description = random_string(20)
        doc = create_course_plan(
            description=description,
            name=name,
            user_id=test_user.id,
        )
        res.append(CoursePlan.model_validate(doc))
    return res


@pytest.fixture
def logged_in_client(test_user, client: FlaskClient):
    with client.session_transaction() as session:
        session["username"] = test_user.username
    yield client


@pytest.mark.parametrize(
    "method, endpoint, body",
    [
        ("GET", ""),
        ("GET", "asd"),
        ("POST", ""),
        ("PATCH", "asd"),
        ("DELETE", "asd"),
    ],
)
def test_unauthenticated_access(client: FlaskClient, method: str, endpoint: str):
    base_url = "/api/course-plans/"
    response = client.open(f"{base_url}{endpoint}", method=method)
    assert response.status_code == 401
    course_plan_response = CoursePlanResponseModel.model_validate(response.json)
    assert course_plan_response.status == "ERROR"
    assert course_plan_response.error == "Unauthorized"


def test_create_course_plan(logged_in_client, test_user):
    for _ in range(20):
        plan = CoursePlan(
            description=random_string(20),
            name=random_string(),
            user_id=test_user.id,
            favourite=False,
            updated_at=datetime.now(timezone.utc),
        )
        response = logged_in_client.post("/api/course-plans/", json=plan.model_dump())
        assert response.status_code == 200
        course_plan_response = CoursePlanResponseModel.model_validate(response.json)
        assert course_plan_response.status == "OK"
        assert abs(course_plan_response.data.updated_at - plan.updated_at) < timedelta(
            seconds=1
        )
        plan.id = course_plan_response.data.id
        course_plan_response.data.updated_at = plan.updated_at
        assert plan == CoursePlan.model_validate(
            course_plan_response.data.model_dump(exclude={"_id"})
        )


def test_get_zero_course_plans(logged_in_client):
    response = logged_in_client.get("/api/course-plans/")
    assert response.status_code == 200
    course_plan_response = CoursePlanResponseModel.model_validate(response.json)
    assert course_plan_response.status == "OK"
    assert isinstance(course_plan_response.data, list)
    assert len(course_plan_response.data) == 0


def test_get_all_course_plans(logged_in_client, course_plans):
    response = logged_in_client.get("/api/course-plans/")
    assert response.status_code == 200
    course_plan_response = CoursePlanResponseModel.model_validate(response.json)
    assert course_plan_response.status == "OK"
    assert isinstance(course_plan_response.data, list)
    assert len(course_plan_response.data) == 20
    for plan in course_plans:
        assert (
            CoursePlanRead.model_validate(plan.model_dump())
            in course_plan_response.data
        )


def test_get_course_plan(logged_in_client, course_plans):
    for plan in course_plans:
        response = logged_in_client.get(f"/api/course-plans/{plan.id}")
        assert response.status_code == 200
        course_plans_response = CoursePlanResponseModel.model_validate(response.json)
        assert course_plans_response.status == "OK"
        assert (
            CoursePlanRead.model_validate(plan.model_dump())
            == course_plans_response.data
        )


def update_subtest(
    plan, logged_in_client, update_obj: CoursePlanUpdate, check_fields: list[str] = []
):
    original_doc = CoursePlanResponseModel.model_validate(
        logged_in_client.get(f"/api/course-plans/{plan.id}").json
    )
    response = logged_in_client.patch(
        f"/api/course-plans/{plan.id}", json=update_obj.model_dump()
    )
    assert response.status_code == 200
    course_plans_response = CoursePlanResponseModel.model_validate(response.json)
    assert course_plans_response.status == "OK"
    assert isinstance(course_plans_response.data, CoursePlanRead)
    assert abs(
        course_plans_response.data.updated_at - datetime.now(timezone.utc)
    ) < timedelta(seconds=1)
    update_obj.updated_at = course_plans_response.data.updated_at
    # Exclude fields that are not updated for comparison
    assert (
        CoursePlanUpdate.model_validate(
            course_plans_response.data.model_dump(
                include=update_obj.model_dump(exclude_none=True).keys()
            )
        )
        == update_obj
    )
    # Check un-updated fields
    for field in check_fields:
        assert (
            course_plans_response.data.model_dump()[field]
            == original_doc.data.model_dump()[field]
        )


def test_update_course_plan_with_no_change(logged_in_client, course_plans):
    for plan in course_plans:
        # Test update with no change to content
        update_obj = CoursePlanUpdate(
            description=plan.description,
            favourite=plan.favourite,
            name=plan.name,
        )
        update_subtest(plan, logged_in_client, update_obj)


def test_update_course_plan_with_description_name_change(
    logged_in_client, course_plans
):
    for plan in course_plans:
        # Test partial update with changes to description and name
        update_obj = CoursePlanUpdate(
            description=random_string(),
            name=random_string(),
        )
        update_subtest(plan, logged_in_client, update_obj, ["favourite"])


def test_update_course_plan_with_favourite_change(logged_in_client, course_plans):
    for plan in course_plans:
        # Test partial update with changes to favourite
        update_obj = CoursePlanUpdate(
            favourite=False,
        )
        update_subtest(plan, logged_in_client, update_obj, ["description", "name"])
        # Test partial update with changes to favourite
        update_obj = CoursePlanUpdate(
            favourite=True,
        )
        update_subtest(plan, logged_in_client, update_obj, ["description", "name"])


def test_update_course_plan_with_all_change(logged_in_client, course_plans):
    for plan in course_plans:
        # Test update with changes to everything
        update_obj = CoursePlanUpdate(
            description=random_string(),
            favourite=not plan.favourite,
            name=random_string(),
        )
        update_subtest(plan, logged_in_client, update_obj)


def test_update_course_plan_with_original_data(logged_in_client, course_plans):
    for plan in course_plans:
        # Test update with original properties
        update_obj = CoursePlanUpdate(
            description=plan.description,
            favourite=plan.favourite,
            name=plan.name,
        )
        update_subtest(plan, logged_in_client, update_obj)


def test_delete_course_plan(logged_in_client, course_plans):
    for plan in course_plans:
        response = logged_in_client.delete(f"/api/course-plans/{plan.id}")
        assert response.status_code == 200
        course_plan_response = CoursePlanResponseModel.model_validate(response.json)
        assert course_plan_response.status == "OK"
        assert course_plan_response.data is None

        # Test deleting non-existing documents
        response = logged_in_client.delete(f"/api/course-plans/{plan.id}")
        assert response.status_code == 404
        course_plan_response = CoursePlanResponseModel.model_validate(response.json)
        assert course_plan_response.status == "ERROR"

    # Test getting all course plans after deletion
    response = logged_in_client.get("/api/course-plans/")
    assert response.status_code == 200
    course_plan_response = CoursePlanResponseModel.model_validate(response.json)
    assert course_plan_response.status == "OK"
    assert len(course_plan_response.data) == 0


def test_unauthorised_access(logged_in_client, test_user2):
    unauthorised_plan = create_course_plan(
        description=random_string(), name=random_string(), user_id=test_user2.id
    )
    get_all_res = logged_in_client.get("/api/course-plans/")
    assert unauthorised_plan.id not in [
        plan.id
        for plan in CoursePlanResponseModel.model_validate(get_all_res.json).data
    ]
    get_res = logged_in_client.get(f"/api/course-plans/{unauthorised_plan.id}")
    patch_res = logged_in_client.patch(
        f"/api/course-plans/{unauthorised_plan.id}",
        json=CoursePlanUpdate(
            description=random_string(),
            name=random_string(),
            favourite=random.choice([False, True]),
        ).model_dump(),
    )
    delete_res = logged_in_client.delete(f"/api/course-plans/{unauthorised_plan.id}")
    assert get_res.status_code != 200
    assert CoursePlanResponseModel.model_validate(get_res.json).status == "ERROR"
    assert patch_res.status_code != 200
    assert CoursePlanResponseModel.model_validate(patch_res.json).status == "ERROR"
    assert delete_res.status_code != 200
    assert CoursePlanResponseModel.model_validate(delete_res.json).status == "ERROR"
