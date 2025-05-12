import random
from datetime import datetime, timedelta, timezone

import pytest
from flask.testing import FlaskClient

from flaskr.api.exceptions import NotFound, Unauthorized
from flaskr.api.respmodels import (
    CoursePlanResponseModel,
    CoursePlanWithSemestersResponseModel,
    ResponseModel,
)
from flaskr.db.course_plans import create_course_plan
from flaskr.db.semester_plans import create_semester_plan
from flaskr.db.models import CoursePlan, CoursePlanRead, CoursePlanUpdate, User
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
def course_plans(test_user: User) -> list[CoursePlan]:
    assert test_user.id is not None
    res: list[CoursePlan] = []
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
def logged_in_client(test_user: User, client: FlaskClient):
    with client.session_transaction() as session:
        session["username"] = test_user.username
    yield client


@pytest.mark.parametrize(
    "method, endpoint",
    [
        ("GET", ""),
        ("GET", "id"),
        ("POST", ""),
        ("PATCH", "id"),
        ("DELETE", "id"),
    ],
)
def test_unauthenticated_access(client: FlaskClient, method: str, endpoint: str):
    base_url = "/api/course-plans/"
    response = client.open(f"{base_url}{endpoint}", method=method)
    assert response.status_code == Unauthorized.status_code
    course_plan_response = ResponseModel.model_validate(response.json)
    assert course_plan_response.status == "ERROR"
    assert isinstance(course_plan_response.error, Unauthorized)


def test_create_course_plan(logged_in_client: FlaskClient, test_user: User):
    for _ in range(20):
        plan = CoursePlan(
            description=random_string(20),
            name=random_string(),
            user_id=test_user.id,
            favourite=False,
            updated_at=datetime.now(timezone.utc),
        )
        response = logged_in_client.post(
            "/api/course-plans/", json=plan.model_dump(mode="json")
        )
        assert response.status_code == 200
        course_plan_response = CoursePlanResponseModel.model_validate(response.json)
        assert course_plan_response.status == "OK"
        assert isinstance(course_plan_response.data, CoursePlanRead)
        assert abs(course_plan_response.data.updated_at - plan.updated_at) < timedelta(
            seconds=1
        )
        plan.id = course_plan_response.data.id
        course_plan_response.data.updated_at = plan.updated_at
        assert plan == CoursePlan.model_validate(
            course_plan_response.data.model_dump(exclude={"_id"})
        )


def test_get_zero_course_plans(logged_in_client: FlaskClient):
    response = logged_in_client.get("/api/course-plans/")
    assert response.status_code == 200
    course_plan_response = CoursePlanResponseModel.model_validate(response.json)
    assert course_plan_response.status == "OK"
    assert isinstance(course_plan_response.data, list)
    assert len(course_plan_response.data) == 0


def test_get_all_course_plans(
    logged_in_client: FlaskClient, course_plans: list[CoursePlan]
):
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


def test_get_course_plan(logged_in_client: FlaskClient, course_plans: list[CoursePlan]):
    for plan in course_plans:
        response = logged_in_client.get(f"/api/course-plans/{plan.id}")
        assert response.status_code == 200
        course_plans_response = CoursePlanWithSemestersResponseModel.model_validate(
            response.json
        )
        assert course_plans_response.status == "OK"
        assert hasattr(course_plans_response.data, "course_plan")
        assert hasattr(course_plans_response.data, "semester_plans")
        assert course_plans_response.data is not None
        assert CoursePlanRead.model_validate(
            plan.model_dump()
        ) == CoursePlanRead.model_validate(
            course_plans_response.data.course_plan.model_dump()
        )
        assert isinstance(course_plans_response.data.semester_plans, list)


def update_subtest(
    plan: CoursePlan,
    logged_in_client: FlaskClient,
    update_obj: CoursePlanUpdate,
    check_fields: list[str] = [],
):
    # Use the new response model for GET
    original_doc = CoursePlanWithSemestersResponseModel.model_validate(
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
                include=set(update_obj.model_dump(exclude_none=True).keys())
            )
        )
        == update_obj
    )
    assert original_doc.data is not None
    # Check un-updated fields
    for field in check_fields:
        # Convert to CoursePlanRead for comparison
        original_course_plan = CoursePlanRead.model_validate(
            original_doc.data.course_plan.model_dump()
        )
        assert (
            course_plans_response.data.model_dump()[field]
            == original_course_plan.model_dump()[field]
        )


def test_update_course_plan_with_no_change(
    logged_in_client: FlaskClient, course_plans: list[CoursePlan]
):
    for plan in course_plans:
        # Test update with no change to content
        update_obj = CoursePlanUpdate(
            description=plan.description,
            favourite=plan.favourite,
            name=plan.name,
        )
        update_subtest(plan, logged_in_client, update_obj)


def test_update_course_plan_with_description_name_change(
    logged_in_client: FlaskClient, course_plans: list[CoursePlan]
):
    for plan in course_plans:
        # Test partial update with changes to description and name
        update_obj = CoursePlanUpdate(
            description=random_string(),
            name=random_string(),
        )
        update_subtest(plan, logged_in_client, update_obj, ["favourite"])


def test_update_course_plan_with_favourite_change(
    logged_in_client: FlaskClient, course_plans: list[CoursePlan]
):
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


def test_update_course_plan_with_all_change(
    logged_in_client: FlaskClient, course_plans: list[CoursePlan]
):
    for plan in course_plans:
        # Test update with changes to everything
        update_obj = CoursePlanUpdate(
            description=random_string(),
            favourite=not plan.favourite,
            name=random_string(),
        )
        update_subtest(plan, logged_in_client, update_obj)


def test_update_course_plan_with_original_data(
    logged_in_client: FlaskClient, course_plans: list[CoursePlan]
):
    for plan in course_plans:
        # Test update with original properties
        update_obj = CoursePlanUpdate(
            description=plan.description,
            favourite=plan.favourite,
            name=plan.name,
        )
        update_subtest(plan, logged_in_client, update_obj)


def test_delete_course_plan(
    logged_in_client: FlaskClient, course_plans: list[CoursePlan]
):
    for plan in course_plans:
        # Create some semester plans for this course plan
        semester_plans = []
        for semester in range(1, 4):  # Create plans for semesters 1, 2, and 3
            semester_plan = create_semester_plan(
                course_plan_id=plan.id,
                semester=semester,
                year=2025,
            )
            assert semester_plan is not None
            semester_plans.append(semester_plan)

        # Get semester plans before deletion to verify they exist
        pre_delete_response = logged_in_client.get(f"/api/course-plans/{plan.id}")
        assert pre_delete_response.status_code == 200
        pre_delete_data = CoursePlanWithSemestersResponseModel.model_validate(
            pre_delete_response.json
        )
        assert isinstance(pre_delete_data.data.semester_plans, list)
        assert len(pre_delete_data.data.semester_plans) == 3

        # Delete the course plan
        response = logged_in_client.delete(f"/api/course-plans/{plan.id}")
        assert response.status_code == 200
        course_plan_response = CoursePlanResponseModel.model_validate(response.json)
        assert course_plan_response.status == "OK"
        assert course_plan_response.data is None

        # Test deleting non-existing documents
        response = logged_in_client.delete(f"/api/course-plans/{plan.id}")
        assert response.status_code == NotFound.status_code
        course_plan_response = CoursePlanResponseModel.model_validate(response.json)
        assert course_plan_response.status == "ERROR"
        assert isinstance(course_plan_response.error, NotFound)

        # Verify that associated semester plans are also deleted
        post_delete_response = logged_in_client.get(f"/api/course-plans/{plan.id}")
        assert post_delete_response.status_code == NotFound.status_code

        # All semester plans should be deleted
        for semester_plan in semester_plans:
            response = logged_in_client.get(f"/api/semester-plans/{semester_plan.id}")
            assert response.status_code == NotFound.status_code

    # Test getting all course plans after deletion
    response = logged_in_client.get("/api/course-plans/")
    assert response.status_code == 200
    course_plan_response = CoursePlanResponseModel.model_validate(response.json)
    assert course_plan_response.status == "OK"
    assert isinstance(course_plan_response.data, list)
    assert len(course_plan_response.data) == 0


def test_unauthorised_access(logged_in_client: FlaskClient, test_user2: User):
    assert test_user2.id is not None
    unauthorised_plan = create_course_plan(
        description=random_string(), name=random_string(), user_id=test_user2.id
    )
    assert unauthorised_plan is not None
    get_all_res = CoursePlanResponseModel.model_validate(
        logged_in_client.get("/api/course-plans/").json
    )
    assert isinstance(get_all_res.data, list)
    assert unauthorised_plan.id not in [plan.id for plan in get_all_res.data]
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
