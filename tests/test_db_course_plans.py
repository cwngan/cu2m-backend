import random
import pytest

from flaskr.db.course_plans import (
    create_course_plan,
    delete_course_plan,
    get_course_plan,
    update_course_plan,
)
from flaskr.db.models import CoursePlan, CoursePlanUpdate
from tests.utils import random_string, random_user


@pytest.fixture(scope="module")
def course_plan_test_user():
    """
    Create a test user for course plan tests.
    """
    from flaskr.db.database import get_db

    user = random_user()
    user.id = get_db().users.insert_one(user.model_dump(exclude_none=True)).inserted_id
    return user


@pytest.fixture(scope="module")
def course_plans() -> list[CoursePlan]:
    """
    Create a list of course plans for the test user.
    """
    res = []
    return res


def test_create_course_plan(course_plan_test_user, course_plans):
    """
    Test creating a course plan.
    """
    from flaskr.db.database import get_db

    db_course_plans = get_db().course_plans
    for i in range(20):
        name = random_string()
        description = random_string(20)
        doc = create_course_plan(
            description=description, name=name, user_id=course_plan_test_user.id
        )
        assert doc is not None
        course_plans.append(doc)
        doc_count = db_course_plans.count_documents(
            {"user_id": course_plan_test_user.id}
        )
        assert doc_count == i + 1
    assert len(course_plans) == 20
    db_course_plans_docs_cursor = db_course_plans.find(
        {"user_id": course_plan_test_user.id}
    )
    db_course_plans_docs = [
        CoursePlan.model_validate(doc) for doc in db_course_plans_docs_cursor
    ]
    assert len(db_course_plans_docs) == 20
    for doc in db_course_plans_docs:
        assert doc in course_plans


def test_get_course_plan(course_plans):
    """
    Test fetching course plans.
    """
    for course_plan in course_plans:
        db_plan = get_course_plan(course_plan.id)
        assert db_plan == course_plan


def test_update_course_plan(course_plans):
    """
    Test updating course plans.
    """
    for course_plan in course_plans:
        new_name = random_string(random.randint(10, 30))
        new_desc = random_string(random.randint(10, 30))
        favourite = random.choice([False, True])
        update_course_plan(
            course_plan.id,
            CoursePlanUpdate(
                description=new_desc,
            ),
        )
        course_plan.description = new_desc
        assert get_course_plan(course_plan.id) == course_plan
        update_course_plan(
            course_plan.id,
            CoursePlanUpdate(
                name=new_name,
                favourite=favourite,
            ),
        )
        course_plan.name = new_name
        course_plan.favourite = favourite
        assert get_course_plan(course_plan.id) == course_plan
        update_course_plan(
            course_plan.id,
            CoursePlanUpdate(
                favourite=(not favourite),
            ),
        )
        course_plan.favourite = not favourite
        assert get_course_plan(course_plan.id) == course_plan


def test_delete_course_plan(course_plans):
    """
    Test deleting course plans.
    """
    from flaskr.db.database import get_db

    db_course_plans = get_db().course_plans
    for idx, course_plan in enumerate(course_plans):
        delete_course_plan(course_plan.id)
        assert get_course_plan(course_plan.id) is None
        assert db_course_plans.count_documents({}) == len(course_plans) - idx - 1
