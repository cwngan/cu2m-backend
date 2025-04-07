import os
import json
from pymongo import MongoClient
from types import SimpleNamespace
from jsonschema import validate


_mongo = None

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


def get_db():
    global _mongo
    if not _mongo:
        from dotenv import load_dotenv

        load_dotenv()
        import sys

        print(os.getenv("DEBUG"), file=sys.stdout)
        mongo_uri = ""
        if os.getenv("DEBUG"):
            mongo_uri = "mongodb://localhost:27017/"
        else:
            mongo_uri = f"mongodb://{os.getenv('MONGO_DB_USERNAME')}:{os.getenv('MONGO_DB_PASSWORD')}@mongodb:27017/"

        _mongo = MongoClient(mongo_uri)
    return _mongo.database
