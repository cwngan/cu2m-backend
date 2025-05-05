from bson import ObjectId
from flaskr.db.database import get_db


def get_all_courses(projection: dict[str, bool], after: ObjectId, limit: int):
    courses_collection = get_db().courses
    return courses_collection.find(
        {"_id": {"$gt": after}}, projection=projection
    ).limit(limit)


def get_courses(
    keywords: list[str], projection: dict[str, bool], after: ObjectId, limit: int
):
    courses_collection = get_db().courses
    result = []
    # Search priority: first by code, then by title, then by description

    # Search by code
    if limit > 0:
        result += (
            courses_collection.find(
                {
                    "code": {
                        "$regex": "|".join(["^" + keyword for keyword in keywords]),
                        "$options": "i",
                    },
                    "_id": {"$gt": after},
                },
                projection=projection,
            )
            .limit(limit)
            .to_list()
        )
    limit -= len(result)

    if limit > 0:
        result += (
            courses_collection.find(
                {
                    "$text": {
                        "$search": " ".join(f'"{keyword}"' for keyword in keywords)
                    }
                },
                projection=projection,
            )
            .sort({"score": {"$meta": "textScore"}})
            .limit(limit)
            .to_list()
        )

    return result
