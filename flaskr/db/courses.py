from flaskr.db.database import get_db


def get_all_courses():
    coursesdb = get_db().courses
    # print(">> COURSES ", coursesdb.find({}).to_list(), flush=True)
    return coursesdb.find({}).to_list()


def get_courses(patterns: list[str]):
    coursesdb = get_db().courses
    return coursesdb.find(
        {
            "code": {
                "$regex": "|".join(["^" + pattern for pattern in patterns]),
                "$options": "i",
            }
        }
    )
