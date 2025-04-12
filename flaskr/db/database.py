import os
from typing import Any

from pymongo import MongoClient

# from flask import current_app

_mongo: MongoClient[dict[str, Any]] | None = None


def init_db():
    db = get_db()
    db.users.create_index("email", unique=True)
    db.users.create_index("username", unique=True, sparse=True)
    db.tokens.create_index("token", unique=True)
    db.tokens.create_index("expires_at", expireAfterSeconds=0)


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
        print(_mongo)
    return _mongo


def get_db():
    return get_mongo_client().database
