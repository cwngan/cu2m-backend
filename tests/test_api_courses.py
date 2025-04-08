import pytest

from flask.testing import FlaskClient

from flaskr.db.models import Course


@pytest.mark.parametrize(
    "input, expected",
    [
        ("ENGG1110", "Problem Solving By Programming"),
        ("CSCI2100", "Data Structures"),
        ("ESTR2102", "Data Structures"),
        ("CSCI3100", "Software Engineering"),
    ],
)
def test_single_exact_course_code(client: FlaskClient, input, expected):
    """
    Test if the given exact course code returns the exact expected name
    """
    response = client.get(f"/api/courses/?code={input}")
    assert response.status_code == 200
    data = response.json
    assert data.get("status") == "OK"
    courses = data.get("data")
    assert len(courses) == 1
    assert courses[0].get("code") == input
    assert courses[0].get("title") == expected


@pytest.mark.parametrize(
    "input",
    [
        (["ENGG1110", "CSCI3100"]),
        (["ENGG", "CSCI", "CENG", "MATH"]),
        (["E", "LING"]),
    ],
)
def test_multiple_prefix_course_code(client: FlaskClient, input):
    """
    Test if the multiple prefix course code returns the all the courses with either prefix
    """
    response = client.get(f"/api/courses/?{'&'.join(f'code={x}' for x in input)}")
    assert response.status_code == 200
    data = response.json
    assert data.get("status") == "OK"
    courses = data.get("data")
    for course in courses:
        assert course.get("code").startswith(input)


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
def test_invalid_prefix_course_code(client: FlaskClient, input):
    """
    Test if the multiple prefix course code returns the all the courses with either prefix
    """
    response = client.get(f"/api/courses/?{'&'.join(f'code={x}' for x in input)}")
    assert response.status_code == 200
    data = response.json
    assert data.get("status") == "ERROR"
    assert data.get("error") == "Invalid course code prefix."


def test_courses_match_schema(client: FlaskClient):
    response = client.get("/api/courses")

    assert response.status_code == 200
    data = response.json
    assert data.get("status") == "OK"
    courses = data.get("data")
    for course in courses:
        res = Course.model_validate(courses)
        assert res.status == "OK"
