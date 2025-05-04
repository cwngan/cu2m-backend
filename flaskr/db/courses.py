from bson import ObjectId
from flaskr.db.database import get_db


def get_all_courses(projection: dict[str, bool], after: ObjectId, limit: int):
    courses_collection = get_db().courses
    return courses_collection.find(
        {"_id": {"$gt": after}}, projection=projection
    ).limit(limit)


def get_courses(
    patterns: list[str], projection: dict[str, bool], after: ObjectId, limit: int
):
    courses_collection = get_db().courses
    return courses_collection.find(
        {
            "code": {
                "$regex": "|".join(["^" + pattern for pattern in patterns]),
                "$options": "i",
            },
            "_id": {"$gt": after},
        },
        projection=projection,
    ).limit(limit)
