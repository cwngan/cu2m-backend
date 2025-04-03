import os
import json
from pymongo import MongoClient
from types import SimpleNamespace


_mongo = None


def init_db():
    db = get_db()
    db_course_version_config = db.config.find_one({"key": "course_version"})
    req_fmt = json.load(open("req_fmt.json"))
    if not db_course_version_config or db_course_version_config.get("value") < req_fmt.get("version"):
        db.config.find_one_and_update({"key": "course_version"}, {"$set": {"value": req_fmt.get("version")}}, upsert=True)
        db.courses.drop()
        db.courses.create_index("code", unique=True)
        json_courses = req_fmt.get("data")
        for json_course in json_courses.values():
            json_string = json.dumps(json_course.get("data"))
            course = json.loads(json_string, object_hook=lambda d: SimpleNamespace(**d))
            course.original, course.parsed = '\n'.join(json_course.get("original")), json_course.get("parsed")
            db.courses.update_one({"code": course.code}, {"$set": course.__dict__}, upsert=True)


def get_db():
    global _mongo
    if not _mongo:
        from dotenv import load_dotenv
        
        load_dotenv()
        mongo_uri = f"mongodb://{os.getenv("MONGO_DB_USERNAME")}:{os.getenv("MONGO_DB_PASSWORD")}@mongodb:27017/"
        _mongo = MongoClient(mongo_uri)
    return _mongo.database
