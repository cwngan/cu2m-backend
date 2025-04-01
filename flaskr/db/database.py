import os
from pymongo import MongoClient

_mongo = None

def get_db():
    global _mongo
    if not _mongo:
        mongo_uri = f"mongodb://{os.getenv("MONGO_DB_USERNAME")}:{os.getenv("MONGO_DB_PASSWORD")}@mongodb:27017/"
        from dotenv import load_dotenv
        
        load_dotenv
        _mongo = MongoClient(mongo_uri)
    return _mongo.database
