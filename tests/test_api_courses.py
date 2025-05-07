import json
import os
import pytest

from flask.testing import FlaskClient

from flaskr.api.respmodels import CoursesResponseModel
from flaskr.db.models import Course


@pytest.mark.parametrize(
    "input, expected",
    [
        ("MATH2028", "Honours Advanced Calculus II"),
        ("PHED1073", "Badminton"),
        ("PHED1042", "Badminton"),
        ("CSCI3100", "Software Engineering"),
    ],
)
def test_single_exact_course_code(client: FlaskClient, input, expected):
    """
    Test if the given exact course code returns the exact expected name for the first entry
    """
    response = client.get(f"/api/courses/?keywords={input}")
    assert response.status_code == 200
    res = CoursesResponseModel.model_validate(response.json)
    assert res.status == "OK"
    courses = res.data
    assert len(courses) == 1
    assert courses[0].code == input
    assert courses[0].title == expected


@pytest.mark.parametrize(
    "input",
    [
        (["ENGG1110", "CSCI3100"]),
        (["ENGG", "CSCI", "CENG", "MATH"]),
        (["engiNEERing", "matheMAtics"]),
    ],
)
def test_multiple_keywords(client: FlaskClient, input):
    """
    Test if the multiple prefix course code returns the all the courses with either prefix
    """
    response = client.get(f"/api/courses/?{'&'.join(f'keywords={x}' for x in input)}")
    assert response.status_code == 200
    res = CoursesResponseModel.model_validate(response.json)
    assert res.status == "OK"
    assert len(res.data) >= 1
    for course in res.data:
        ok = False
        for keyword in input:
            if course.code.startswith(keyword):
                ok = True
                break
            elif (
                keyword.lower() in course.description.lower()
                or keyword.lower() in course.title.lower()
            ):
                ok = True
                break
        assert ok


def test_all_courses_match_schema(client: FlaskClient):
    response = client.get("/api/courses/?limit=2147483647")

    assert response.status_code == 200
    res = CoursesResponseModel.model_validate(response.json)
    assert res.status == "OK"

    course_data_filename = os.getenv("COURSE_DATA_FILENAME")
    course_data = json.load(open(course_data_filename))
    assert len(course_data.get("data").items()) == len(res.data)


@pytest.mark.parametrize(
    "test_mode",
    [(None), ("includes"), ("excludes")],
)
def test_course_fetch_basic_flag(test_mode, client: FlaskClient):
    response = client.get(
        f"/api/courses/?basic=true&{test_mode}=code"
        if test_mode
        else "/api/courses/?basic=true"
    )

    assert response.status_code == 200
    res = CoursesResponseModel.model_validate(response.json)
    assert res.status == "OK"

    assert False not in map(
        lambda course: set(course.model_dump(exclude_none=True, by_alias=False).keys())
        == set(("id", "code", "title", "units")),
        res.data,
    )


@pytest.mark.parametrize(
    "includes",
    [
        (["code", "id"]),
        (["code", "units", "foo", "bar"]),
    ],
)
def test_course_fetch_includes_list(includes: list[str], client: FlaskClient):
    response = client.get(
        "/api/courses/?{includes}".format(
            includes="&".join(f"includes={include}" for include in includes)
        )
    )

    # Obtain fields that are actually used
    actual_includes = set(includes) & set(Course.model_fields.keys())
    # ID will always be returned
    actual_includes.add("id")

    assert response.status_code == 200
    res = CoursesResponseModel.model_validate(response.json)
    assert res.status == "OK"

    assert False not in map(
        lambda course: set(course.model_dump(exclude_none=True, by_alias=False).keys())
        == actual_includes,
        res.data,
    )


@pytest.mark.parametrize(
    "excludes",
    [
        (["description", "original"]),
        (["prerequisites", "corequisites", "foo", "bar"]),
        (["_id", "id"]),  # Make sure id field is always here
    ],
)
def test_course_fetch_excludes_list(excludes: list[str], client: FlaskClient):
    response = client.get(
        "/api/courses/?{excludes}".format(
            excludes="&".join(f"excludes={exclude}" for exclude in excludes)
        )
    )

    # Obtain fields that are actually used
    actual_includes = set(Course.model_fields.keys()) - set(excludes)
    # ID will always be returned
    actual_includes.add("id")

    assert response.status_code == 200
    res = CoursesResponseModel.model_validate(response.json)
    assert res.status == "OK"

    assert False not in map(
        lambda course: set(course.model_dump(exclude_none=True, by_alias=False).keys())
        == actual_includes,
        res.data,
    )


@pytest.mark.parametrize(
    "value, valid",
    [("true", True), ("FaLsE", True), ("Flase", False), ("Bruh", False)],
)
def test_flag_boolean_validation(value, valid, client: FlaskClient):
    for flag in ["basic", "strict"]:
        response = client.get(f"/api/courses/?{flag}={value}")

        res = CoursesResponseModel.model_validate(response.json)
        if valid:
            assert response.status_code == 200
            assert res.status == "OK"
        else:
            assert response.status_code == 400
            assert res.status == "ERROR"


def test_includes_excludes_conflict(client: FlaskClient):
    response = client.get("/api/courses/?includes=hello&excludes=world")
    assert response.status_code == 400
    res = CoursesResponseModel.model_validate(response.json)
    assert res.status == "ERROR"


def test_courses_pagination(client: FlaskClient):
    response = client.get("/api/courses/?limit=2")
    assert response.status_code == 200
    res = CoursesResponseModel.model_validate(response.json)
    assert res.status == "OK"
    first = res.data

    response = client.get("/api/courses/?limit=2&page=2")
    assert response.status_code == 200
    res = CoursesResponseModel.model_validate(response.json)
    assert res.status == "OK"
    second = res.data

    response = client.get("/api/courses/?limit=4")
    assert response.status_code == 200
    res = CoursesResponseModel.model_validate(response.json)
    assert res.status == "OK"
    answer = res.data

    # Confirm our order is right
    assert first + second == answer


def test_course_pagination_with_large_after(client: FlaskClient):
    response = client.get("/api/courses/?page=2147483647")
    assert response.status_code == 200
    res = CoursesResponseModel.model_validate(response.json)
    assert res.status == "OK"
    assert res.data == []


def test_course_pagination_with_invalid_after(client: FlaskClient):
    response = client.get("/api/courses/?page=foobar")
    assert response.status_code == 400
    res = CoursesResponseModel.model_validate(response.json)
    assert res.status == "ERROR"


@pytest.mark.parametrize(
    "limit, page, valid",
    [
        (1, 1, True),
        (1, 0, False),
        (0, 1, False),
        (2147483647, 1, True),
        (1, 2147483647, True),
        (2147483648, 1, False),
        (1, 2147483648, False),
        (-1, 1, False),
        (1, -1, False),
    ],
)
def test_course_fetch_limit_value(limit, page, valid, client: FlaskClient):
    response = client.get(f"/api/courses/?limit={limit}&page={page}")
    res = CoursesResponseModel.model_validate(response.json)
    if valid:
        assert response.status_code == 200
        assert res.status == "OK"
        assert len(res.data) <= limit
    else:
        assert response.status_code == 400
        assert res.status == "ERROR"
