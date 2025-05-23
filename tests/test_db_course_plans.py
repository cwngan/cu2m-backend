import random
from datetime import datetime, timedelta, timezone

import pytest

from flaskr.db.course_plans import (
    create_course_plan,
    delete_course_plan,
    get_course_plan,
    update_course_plan,
)
from flaskr.db.models import CoursePlan, CoursePlanUpdate, User
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


def test_create_course_plan(test_user: User, get_db: GetDatabase):
    """
    Test creating a course plan.
    """
    assert test_user.id is not None
    db_course_plans = get_db().course_plans
    course_plans: list[CoursePlan] = []
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


def test_get_course_plan(course_plans: list[CoursePlan], test_user: User):
    """
    Test fetching course plans.
    """
    assert test_user.id is not None
    for course_plan in course_plans:
        assert course_plan.id is not None
        db_plan = get_course_plan(course_plan.id, test_user.id)
        assert db_plan == course_plan


def test_update_course_plan(course_plans: list[CoursePlan], test_user: User):
    """
    Test updating course plans.
    """
    assert test_user.id is not None
    for course_plan in course_plans:
        assert course_plan.id is not None
        new_name = random_string(random.randint(10, 30))
        new_desc = random_string(random.randint(10, 30))
        favourite = random.choice([False, True])
        update_course_plan(
            course_plan.id,
            CoursePlanUpdate(
                name=course_plan.name,
                description=new_desc,
                favourite=course_plan.favourite,
            ),
            test_user.id,
        )
        course_plan.description = new_desc
        course_plan.updated_at = datetime.now(timezone.utc)
        db_course_plan = get_course_plan(course_plan.id, test_user.id)
        assert db_course_plan is not None
        assert db_course_plan.model_dump(
            exclude={"updated_at"}
        ) == course_plan.model_dump(exclude={"updated_at"})
        assert abs(db_course_plan.updated_at - course_plan.updated_at) < timedelta(
            seconds=1
        )
        update_course_plan(
            course_plan.id,
            CoursePlanUpdate(
                name=new_name,
                description=course_plan.description,
                favourite=favourite,
            ),
            test_user.id,
        )
        course_plan.name = new_name
        course_plan.favourite = favourite
        ret = get_course_plan(course_plan.id, test_user.id)
        assert ret is not None
        assert ret.model_dump(exclude={"updated_at"}) == course_plan.model_dump(
            exclude={"updated_at"}
        )
        assert abs(db_course_plan.updated_at - course_plan.updated_at) < timedelta(
            seconds=1
        )
        update_course_plan(
            course_plan.id,
            CoursePlanUpdate(
                name=course_plan.name,
                description=course_plan.description,
                favourite=(not favourite),
            ),
            test_user.id,
        )
        course_plan.favourite = not favourite
        ret = get_course_plan(course_plan.id, test_user.id)
        assert ret is not None
        assert ret.model_dump(exclude={"updated_at"}) == course_plan.model_dump(
            exclude={"updated_at"}
        )
        assert abs(db_course_plan.updated_at - course_plan.updated_at) < timedelta(
            seconds=1
        )


def test_delete_course_plan(
    course_plans: list[CoursePlan], test_user: User, get_db: GetDatabase
):
    """
    Test deleting course plans.
    """
    assert test_user.id is not None
    db_course_plans = get_db().course_plans
    for idx, course_plan in enumerate(course_plans):
        assert course_plan.id is not None
        delete_course_plan(course_plan.id, test_user.id)
        assert get_course_plan(course_plan.id, test_user.id) is None
        assert db_course_plans.count_documents({}) == len(course_plans) - idx - 1


def test_unauthorized_access(
    course_plans: list[CoursePlan], test_user: User, get_db: GetDatabase
):
    assert test_user.id is not None
    user2 = random_user()
    user2.id = (
        get_db().users.insert_one(user2.model_dump(exclude_none=True)).inserted_id
    )
    assert user2.id is not None
    new_plan = create_course_plan(random_string(20), random_string(), user2.id)
    assert new_plan is not None
    assert new_plan.id is not None
    assert get_course_plan(new_plan.id, user2.id) == new_plan
    for plan in course_plans:
        assert plan.id is not None
        assert get_course_plan(plan.id, user2.id) is None
    assert get_course_plan(new_plan.id, test_user.id) is None
