from flaskr.db.database import get_db
from flaskr.db.models import Course


def get_all_courses():
    coursesdb = get_db().courses
    return [Course(**course) for course in coursesdb.find({})]


def get_courses(patterns: list[str]):
    coursesdb = get_db().courses
    doc = coursesdb.find(
        {
            "code": {
                "$regex": "|".join(["^" + pattern for pattern in patterns]),
                "$options": "i",
            }
        }
    )
    return [Course(**course) for course in doc]
