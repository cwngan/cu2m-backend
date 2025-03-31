import os
from pymongo import MongoClient

_mongo = None

def get_mongo():
    global _mongo
    if not _mongo:
        mongo_uri = f"mongodb://{os.getenv("MONGO_DB_USERNAME")}:{os.getenv("MONGO_DB_PASSWORD")}@mongodb:27017/"
        _mongo = MongoClient(mongo_uri)
    return _mongo
