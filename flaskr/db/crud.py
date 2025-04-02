from flaskr.db.database import get_db


def get_all_courses(db=get_db()):
    return db.courses.find({}).to_list()


def get_courses(patterns: list[str], db=get_db()):
    return db.courses.find(
        {
            "code": {
                "$regex": "|".join(["^" + pattern for pattern in patterns]),
                "$options": "i",
            }
        }
    )
