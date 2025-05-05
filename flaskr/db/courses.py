from time import time
from flaskr.db.database import get_db
from flaskr.db.database import get_db_logger


def get_all_courses(projection: dict[str, bool], page: int, limit: int):
    courses_collection = get_db().courses
    return (
        courses_collection.find({}, projection=projection)
        .skip((page - 1) * limit)
        .limit(limit)
    )


def get_courses(
    keywords: list[str], projection: dict[str, bool], page: int, limit: int
):
    courses_collection = get_db().courses

    # Time our search for research purpose
    start_time = time()

    # Search priority: first by code, then by title, then by description
    pipeline = [
        {
            "$match": {
                "$or": [
                    {
                        "code": {
                            "$regex": "|".join(["^" + keyword for keyword in keywords]),
                            "$options": "i",
                        }
                    },
                    {
                        "$text": {
                            "$search": " ".join(f'"{keyword}"' for keyword in keywords)
                        }
                    },
                ]
            }
        },
        {
            "$addFields": {
                "overall_score": {
                    "$cond": {
                        "if": {
                            "$regexMatch": {
                                "input": "$code",
                                "regex": "|".join(
                                    ["^" + keyword for keyword in keywords]
                                ),
                                "options": "i",
                            }
                        },
                        "then": 0x3F3F3F3F,
                        "else": {"$meta": "textScore"},
                    }
                }
            }
        },
        {"$sort": {"overall_score": -1}},
        {"$skip": (page - 1) * limit},
        {"$limit": limit},
    ]
    if projection:
        pipeline.append({"$project": projection})

    result = courses_collection.aggregate(pipeline).to_list()

    end_time = time()

    get_db_logger().info(
        "Executed course search on keywords {keywords} with limit {limit} on page {page} using {exec_time:.3f}s".format(
            keywords=keywords, limit=limit, page=page, exec_time=end_time - start_time
        )
    )
    return result
