from flaskr.db.database import get_db


def get_all_courses(projection: dict[str, bool]):
    courses_collection = get_db().courses
    return courses_collection.find({}, projection=projection).to_list()


def get_courses(patterns: list[str], projection: dict[str, bool]):
    courses_collection = get_db().courses
    return courses_collection.find(
        {
            "code": {
                "$regex": "|".join(["^" + pattern for pattern in patterns]),
                "$options": "i",
            }
        },
        projection=projection,
    ).to_list()
