import os
import json
from typing import Any

from pymongo import MongoClient
from types import SimpleNamespace
from jsonschema import validate


_mongo: MongoClient[dict[str, Any]] | None = None

schema = {
    "type": "object",
    "properties": {
        "version": {"type": "integer"},
        "data": {
            "type": "object",
            "patternProperties": {
                r"^[A-Z]{4}[0-9]{4}": {
                    "type": "object",
                    "properties": {
                        "parsed": {"type": "boolean"},
                        "data": {
                            "type": "object",
                            "properties": {
                                "code": {"type": "string"},
                                "corequisites": {"type": "string"},
                                "description": {"type": "string"},
                                "is_graded": {"type": "boolean"},
                                "not_for_major": {"type": "string"},
                                "not_for_taken": {"type": "string"},
                                "prerequisites": {"type": "string"},
                                "title": {"type": "string"},
                                "units": {"type": "number"},
                            },
                            "additionalProperties": False,
                            "minProperties": 9,
                        },
                        "original": {"type": "string"},
                    },
                    "additionalProperties": False,
                    "minProperties": 3,
                },
            },
        },
    },
}


def init_db():
    from dotenv import load_dotenv

    load_dotenv()

    course_data_filename = os.getenv("COURSE_DATA_FILENAME")
    course_data = json.load(open(course_data_filename))

    validate(instance=course_data, schema=schema)

    db = get_db()
    db_course_version_config = db.config.find_one({"key": "course_version"})
    if not db_course_version_config or db_course_version_config.get(
        "value"
    ) < course_data.get("version"):
        db.config.find_one_and_update(
            {"key": "course_version"},
            {"$set": {"value": course_data.get("version")}},
            upsert=True,
        )
        db.courses.drop()
        db.courses.create_index("code", unique=True)
        json_courses = course_data.get("data")
        for json_course in json_courses.values():
            json_string = json.dumps(json_course.get("data"))
            course = json.loads(json_string, object_hook=lambda d: SimpleNamespace(**d))
            course.original, course.parsed = json_course.get(
                "original"
            ), json_course.get("parsed")
            db.courses.update_one(
                {"code": course.code}, {"$set": course.__dict__}, upsert=True
            )
    # print(">> DB ", db.courses.find({}).to_list(), flush=True)
    db.users.create_index("email", unique=True)
    db.users.create_index("username", unique=True, sparse=True)


def get_mongo_client():
    global _mongo
    if not _mongo:
        from dotenv import load_dotenv

        load_dotenv()

        mongo_uri = f"mongodb://{os.getenv('MONGO_DB_USERNAME')}:{os.getenv('MONGO_DB_PASSWORD')}@{os.getenv('MONGO_DB_HOST')}:{os.getenv('MONGO_DB_PORT')}/"
        print(mongo_uri, flush=True)
        _mongo = MongoClient(mongo_uri, tz_aware=True)
        init_db()
        print("MongoDB connected", flush=True)
        print(_mongo, flush=True)
    return _mongo


def get_db():
    return get_mongo_client().database
