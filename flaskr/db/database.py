import os
from typing import Any

from pymongo import MongoClient
from pymongo.database import Database

# from flask import current_app

_mongo = None


def init_db():
    db = get_db()
    db.users.create_index("email", unique=True)
    db.users.create_index("username", unique=True, sparse=True)


def get_db() -> Database[dict[str, Any]]:
    global _mongo
    if not _mongo:
        from dotenv import load_dotenv

        load_dotenv()
        mongo_uri = f"mongodb://{os.getenv('MONGO_DB_USERNAME')}:{os.getenv('MONGO_DB_PASSWORD')}@mongodb:27017/"
        print(mongo_uri, flush=True)
        _mongo = MongoClient(mongo_uri)
        print("MongoDB connected", flush=True)
        print(_mongo)
        print(_mongo.database)
        init_db()

    return _mongo.database
