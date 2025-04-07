import pytest

from flaskr import create_app


@pytest.mark.parametrize(
    "input, expected",
    [
        ("ENGG1110", "Problem Solving By Programming"),
        ("CSCI2100", "Data Structures"),
        ("ESTR2102", "Data Structures"),
        ("CSCI3100", "Software Engineering"),
    ],
)
def test_if_exact_code_gets_exact_course(input, expected):
    """
    Test if the given exact course code returns the exact expected name
    """
    app = create_app()

    with app.test_client() as client:
        response = client.get(f"/api/courses/?code={input}")
        assert (
            response.status_code == 200
        ), f"Invalid status code ({response.status_code} returned)."
        data = response.json
        assert (
            data.get("status") == "OK"
        ), f"Error while accessing this API endpoint (error message: {data.get('error')})."
        courses = data.get("data")
        assert (
            len(courses) == 1
        ), f"Exact course code should only return exactly 1 course ({len(courses)} courses found)."
        assert (
            courses[0].get("code") == input
        ), f"Course code cannot be matched (expected: {input}, found: {courses[0].get('code')})"
        assert (
            courses[0].get("title") == expected
        ), f"Incorrect course tile (expected: {expected}, found: {courses[0].get('title')})"
