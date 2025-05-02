import json
import os

import pytest
from flask.testing import FlaskClient

from flaskr.api.respmodels import CoursesResponseModel


@pytest.mark.parametrize(
    "input, expected",
    [
        ("MATH2028", "Honours Advanced Calculus II"),
        ("PHED1073", "Badminton"),
        ("PHED1042", "Badminton"),
        ("CSCI3100", "Software Engineering"),
    ],
)
def test_single_exact_course_code(client: FlaskClient, input: str, expected: str):
    """
    Test if the given exact course code returns the exact expected name
    """
    response = client.get(f"/api/courses/?code={input}")
    assert response.status_code == 200
    res = CoursesResponseModel.model_validate(response.json)
    assert res.status == "OK"
    courses = res.data
    assert courses is not None
    assert len(courses) == 1
    assert courses[0].code == input
    assert courses[0].title == expected


@pytest.mark.parametrize(
    "input",
    [
        (["ENGG1110", "CSCI3100"]),
        (["ENGG", "CSCI", "CENG", "MATH"]),
        (["E", "C"]),
    ],
)
def test_multiple_prefix_course_code(client: FlaskClient, input: list[str]):
    """
    Test if the multiple prefix course code returns the all the courses with either prefix
    """
    response = client.get(f"/api/courses/?{'&'.join(f'code={x}' for x in input)}")
    assert response.status_code == 200
    res = CoursesResponseModel.model_validate(response.json)
    assert res.status == "OK"
    assert res.data is not None
    assert len(res.data) >= 1
    for course in res.data:
        ok = False
        for prefix in input:
            if course.code.startswith(prefix):
                ok = True
                break
        assert ok


def test_empty_course_code(client: FlaskClient):
    """
    Test if unused course code returns nothing
    """
    response = client.get("/api/courses/?code=ZZZZ")
    assert response.status_code == 200
    res = CoursesResponseModel.model_validate(response.json)
    assert res.status == "OK"
    assert res.data is not None
    assert len(res.data) == 0


@pytest.mark.parametrize(
    "input",
    [
        (["ENGG11101"]),
        (["ENGG11101", "CENG"]),
        (["ENGGG"]),
        (["ENG1"]),
        (["", "CSCI"]),
    ],
)
def test_invalid_prefix_course_code(client: FlaskClient, input: list[str]):
    """
    Test if the multiple prefix course code returns the all the courses with either prefix
    """
    response = client.get(f"/api/courses/?{'&'.join(f'code={x}' for x in input)}")
    assert response.status_code == 400
    res = CoursesResponseModel.model_validate(response.json)
    assert res.status == "ERROR"
    assert res.error == "Invalid course code prefix."


def test_all_courses_match_schema(client: FlaskClient):
    response = client.get("/api/courses/")

    assert response.status_code == 200
    res = CoursesResponseModel.model_validate(response.json)
    assert res.status == "OK"

    course_data_filename = os.getenv("COURSE_DATA_FILENAME")
    assert course_data_filename is not None, "COURSE_DATA_FILENAME is not set"
    course_data = json.load(open(course_data_filename))
    assert res.data is not None
    assert len(course_data.get("data").items()) == len(res.data)
