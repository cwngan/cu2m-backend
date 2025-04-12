from datetime import datetime, timedelta, timezone
import random
from flask.testing import FlaskClient
import pytest

from flaskr.api.respmodels import CoursePlanResponseModel
from flaskr.db.course_plans import create_course_plan
from flaskr.db.models import CoursePlan, CoursePlanRead, CoursePlanUpdate
from tests.utils import random_string, random_user


@pytest.fixture
def test_user():
    """
    Insert a test user into the database before running tests.
    """
    from flaskr.db.database import get_db

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
        assert CoursePlan.model_validate(
            plan.model_dump()
        ) == CoursePlan.model_validate(
            course_plan_response.data.model_dump(exclude={"_id"})
        )


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


def test_update_course_plan(logged_in_client, course_plans):
    for plan in course_plans:

        def _test_for_update(update_obj: CoursePlanUpdate):
            response = logged_in_client.put(
                f"/api/course-plans/{plan.id}", json=update_obj.model_dump()
            )
            assert response.status_code == 200
            course_plans_response = CoursePlanResponseModel.model_validate(
                response.json
            )
            assert course_plans_response.status == "OK"
            assert isinstance(course_plans_response.data, CoursePlanRead)
            assert abs(
                course_plans_response.data.updated_at - update_obj.updated_at
            ) < timedelta(seconds=1)
            update_obj.updated_at = course_plans_response.data.updated_at
            assert (
                CoursePlanUpdate.model_validate(course_plans_response.data.model_dump())
                == update_obj
            )

        # Test update with no change to content
        update_obj = CoursePlanUpdate(
            description=plan.description,
            favourite=plan.favourite,
            name=plan.name,
            updated_at=datetime.now(timezone.utc),
        )
        _test_for_update(update_obj)
        # Test update with changes to description and name
        update_obj = CoursePlanUpdate(
            description=random_string(),
            favourite=plan.favourite,
            name=random_string(),
            updated_at=datetime.now(timezone.utc),
        )
        _test_for_update(update_obj)
        # Test update with changes to favourite
        update_obj = CoursePlanUpdate(
            description=plan.description,
            favourite=False,
            name=plan.name,
            updated_at=datetime.now(timezone.utc),
        )
        _test_for_update(update_obj)
        # Test update with changes to favourite
        update_obj = CoursePlanUpdate(
            description=plan.description,
            favourite=True,
            name=plan.name,
            updated_at=datetime.now(timezone.utc),
        )
        _test_for_update(update_obj)
        # Test update with changes to everything
        update_obj = CoursePlanUpdate(
            description=random_string(),
            favourite=random.choice([True, False]),
            name=random_string(),
            updated_at=datetime.now(timezone.utc),
        )
        _test_for_update(update_obj)
        # Test update with original properties
        update_obj = CoursePlanUpdate(
            description=plan.description,
            favourite=plan.favourite,
            name=plan.name,
            updated_at=datetime.now(timezone.utc),
        )
        _test_for_update(update_obj)
