import json
import os

from flask.testing import FlaskClient

from flaskr.db.database import init_db
from flaskr.api.respmodels import CoursesResponseModel


def test_courses_version_upgrade(client: FlaskClient):
    # Ensure database is pre-initialized with something else
    init_db()

    course_data_filename = os.getenv("COURSE_DATA_FILENAME")
    course_data = json.load(open(course_data_filename))
    version = course_data.get("version")

    new_version = version + 1
    new_data = {
        "ZZZZ9999": {
            "parsed": True,
            "data": {
                "code": "ZZZZ9999",
                "corequisites": "",
                "description": "This is a test course.",
                "is_graded": True,
                "not_for_major": "",
                "not_for_taken": "",
                "prerequisites": "",
                "title": "Honours Advanced Calculus II",
                "units": 3.0,
            },
            "original": "",
        }
    }

    with open("courses_new.json", "w") as f:
        json.dump({"version": new_version, "data": new_data}, f)

    os.environ["COURSE_DATA_FILENAME"] = "courses_new.json"

    init_db()

    os.remove("courses_new.json")

    response = client.get("/api/courses/")
    assert response.status_code == 200
    res = CoursesResponseModel.model_validate(response.json)
    assert res.status == "OK"
    assert len(res.data) == 1

    response = client.get("/api/courses/?keywords=ZZZZ9999")
    assert response.status_code == 200
    res = CoursesResponseModel.model_validate(response.json)
    assert res.status == "OK"
    assert len(res.data) == 1

    response = client.get("/api/courses/?keywords=CSCI3100")
    assert response.status_code == 200
    res = CoursesResponseModel.model_validate(response.json)
    assert res.status == "OK"
    assert len(res.data) == 0

    os.environ["COURSE_DATA_FILENAME"] = course_data_filename
