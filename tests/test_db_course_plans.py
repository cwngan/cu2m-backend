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
def course_plans(test_user):
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


def test_create_course_plan(test_user):
    """
    Test creating a course plan.
    """
    from flaskr.db.database import get_db

    db_course_plans = get_db().course_plans
    course_plans = []
    for i in range(20):
        name = random_string()
        description = random_string(20)
        doc = create_course_plan(
            description=description, name=name, user_id=test_user.id
        )
        assert doc is not None
        course_plans.append(doc)
        doc_count = db_course_plans.count_documents({"user_id": test_user.id})
        assert doc_count == i + 1
    assert len(course_plans) == 20
    db_course_plans_docs_cursor = db_course_plans.find({"user_id": test_user.id})
    db_course_plans_docs = [
        CoursePlan.model_validate(doc) for doc in db_course_plans_docs_cursor
    ]
    assert len(db_course_plans_docs) == 20
    for doc in db_course_plans_docs:
        assert doc in course_plans


def test_get_course_plan(course_plans, test_user):
    """
    Test fetching course plans.
    """
    for course_plan in course_plans:
        db_plan = get_course_plan(course_plan.id, test_user.id)
        assert db_plan == course_plan


def test_update_course_plan(course_plans, test_user):
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
            test_user.id,
        )
        course_plan.description = new_desc
        assert get_course_plan(course_plan.id, test_user.id) == course_plan
        update_course_plan(
            course_plan.id,
            CoursePlanUpdate(
                name=new_name,
                favourite=favourite,
            ),
            test_user.id,
        )
        course_plan.name = new_name
        course_plan.favourite = favourite
        assert get_course_plan(course_plan.id, test_user.id) == course_plan
        update_course_plan(
            course_plan.id,
            CoursePlanUpdate(
                favourite=(not favourite),
            ),
            test_user.id,
        )
        course_plan.favourite = not favourite
        assert get_course_plan(course_plan.id, test_user.id) == course_plan


def test_delete_course_plan(course_plans, test_user):
    """
    Test deleting course plans.
    """
    from flaskr.db.database import get_db

    db_course_plans = get_db().course_plans
    for idx, course_plan in enumerate(course_plans):
        delete_course_plan(course_plan.id, test_user.id)
        assert get_course_plan(course_plan.id, test_user.id) is None
        assert db_course_plans.count_documents({}) == len(course_plans) - idx - 1


def test_unauthorized_access(course_plans, test_user):
    from flaskr.db.database import get_db

    user2 = random_user()
    user2.id = (
        get_db().users.insert_one(user2.model_dump(exclude_none=True)).inserted_id
    )
    new_plan = create_course_plan(random_string(20), random_string(), user2.id)
    assert get_course_plan(new_plan.id, user2.id) == new_plan
    for plan in course_plans:
        assert get_course_plan(plan.id, user2.id) is None
    assert get_course_plan(new_plan.id, test_user.id) is None
