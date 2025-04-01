import os
import json
from pymongo import MongoClient
from types import SimpleNamespace


_mongo = None


def init_db():
    db = get_db()
    db.courses.drop()
    
    db.courses.create_index("code", unique=True)
    json_courses = json.load(open("req_fmt.json"))
    for json_course in json_courses.values():
        json_string = json.dumps(json_course.get("data"))
        course = json.loads(json_string, object_hook=lambda d: SimpleNamespace(**d))
        course.original, course.parsed = json_course.get("parsed"), '\n'.join(json_course.get("original"))
        db.courses.update_one({"code": course.code}, {"$set": course.__dict__}, upsert=True)


def get_db():
    global _mongo
    if not _mongo:
        from dotenv import load_dotenv
        
        load_dotenv()
        mongo_uri = f"mongodb://{os.getenv("MONGO_DB_USERNAME")}:{os.getenv("MONGO_DB_PASSWORD")}@mongodb:27017/"
        _mongo = MongoClient(mongo_uri)
    return _mongo.database
