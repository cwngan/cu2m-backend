from datetime import datetime

import pytest

from flaskr.db.models import CoursePlan, SemesterPlanUpdate, User
from flaskr.db.semester_plans import (
    create_semester_plan,
    delete_semester_plan,
    get_semester_plan,
    update_semester_plan,
)
from tests.utils import GetDatabase, random_string, random_user


@pytest.fixture
def test_user(get_db: GetDatabase):
    user = random_user()
    user.id = get_db().users.insert_one(user.model_dump(exclude_none=True)).inserted_id
    return user


def add_course_plan_for_user(
    course_plan: CoursePlan, test_user: User, get_db: GetDatabase
):
    course_plan_id = (
        get_db().course_plans.insert_one(course_plan.model_dump(exclude_none=True)).inserted_id
    )
    course_plan.id = course_plan_id
    return course_plan


@pytest.fixture
def test_course_plan(test_user: User, get_db: GetDatabase):
    course_plan = CoursePlan(
        description=random_string(20),
        name=random_string(),
        user_id=test_user.id,
        favourite=False,
        updated_at=datetime.now(),
    )
    return add_course_plan_for_user(course_plan, test_user, get_db)


@pytest.fixture
def test_two_course_plans(test_user: User, get_db: GetDatabase):
    course_plans: list[CoursePlan] = []
    for i in range(2):
        course_plan = CoursePlan(
            description=random_string(20),
            name=random_string(),
            user_id=test_user.id,
            favourite=False,
            updated_at=datetime.now(),
        )
        course_plans.append(add_course_plan_for_user(course_plan, test_user, get_db))
    return course_plans


def test_create_semester_plan(
    test_user: User, test_course_plan: CoursePlan, get_db: GetDatabase
):
    assert test_course_plan.id is not None
    semester_plan = create_semester_plan(
        course_plan_id=test_course_plan.id,
        semester=1,
        year=2025,
    )
    assert semester_plan is not None
    assert semester_plan.course_plan_id == test_course_plan.id
    assert semester_plan.semester == 1
    assert semester_plan.year == 2025


def test_get_semester_plan(
    test_user: User, test_course_plan: CoursePlan, get_db: GetDatabase
):
    assert test_course_plan.id is not None
    semester_plan = create_semester_plan(
        course_plan_id=test_course_plan.id,
        semester=1,
        year=2025,
    )
    assert semester_plan is not None
    assert semester_plan.id is not None
    fetched_plan = get_semester_plan(semester_plan.id)
    assert fetched_plan
    assert fetched_plan.id == semester_plan.id
    assert fetched_plan.course_plan_id == semester_plan.course_plan_id


def test_update_semester_plan(
    test_user: User, test_course_plan: CoursePlan, get_db: GetDatabase
):
    assert test_course_plan.id
    semester_plan = create_semester_plan(
        course_plan_id=test_course_plan.id,
        semester=1,
        year=2025,
    )
    assert semester_plan is not None
    assert semester_plan.id is not None
    updates = SemesterPlanUpdate(
        semester=2,
        year=2026,
    )
    updated_plan = update_semester_plan(semester_plan.id, updates)
    assert updated_plan is not None
    assert updated_plan.semester == 2
    assert updated_plan.year == 2026


def test_delete_semester_plan(
    test_user: User, test_course_plan: CoursePlan, get_db: GetDatabase
):
    assert test_course_plan.id is not None
    semester_plan = create_semester_plan(
        course_plan_id=test_course_plan.id,
        semester=1,
        year=2025,
    )
    assert semester_plan is not None
    assert semester_plan.id is not None
    deleted_plan = delete_semester_plan(semester_plan.id)
    assert deleted_plan is not None
    assert deleted_plan.id == semester_plan.id
    assert get_semester_plan(semester_plan.id) is None


@pytest.mark.parametrize(
    "first, second, valid",
    [
        ((1, 2026), (2, 2027), True),
        ((1, 2025), (2, 2025), True),
        ((2, 2024), (3, 2024), True),
        ((1, 2025), (1, 2025), False),
    ],
)
def test_semester_plan_compound_key(
    first: tuple[int, int],
    second: tuple[int, int],
    valid: bool,
    test_user: User,
    test_course_plan: CoursePlan,
    get_db: GetDatabase,
):
    assert test_course_plan.id is not None
    semester, year = first
    assert create_semester_plan(
        course_plan_id=test_course_plan.id,
        semester=semester,
        year=year,
    )

    # Try to insert the second object and check the result
    semester, year = second
    semester_plan = create_semester_plan(
        course_plan_id=test_course_plan.id,
        semester=semester,
        year=year,
    )
    if valid:
        assert semester_plan is not None
    else:
        assert semester_plan is None


def test_different_course_plans_create_same_compound_key_semester_plan(
    test_two_course_plans: list[CoursePlan], get_db: GetDatabase
):
    for test_course_plan in test_two_course_plans:
        assert test_course_plan.id is not None
        semester_plan = create_semester_plan(
            course_plan_id=test_course_plan.id,
            semester=1,
            year=2025,
        )
        assert semester_plan is not None
        assert semester_plan.course_plan_id == test_course_plan.id
        assert semester_plan.semester == 1
        assert semester_plan.year == 2025
