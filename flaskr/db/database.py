import os
from pymongo import MongoClient
from flask import current_app

_mongo = None


def init_db():
    db = get_db()
    db.users.create_index("username", unique=True)


def get_db():
    global _mongo
    if not _mongo:
        from dotenv import load_dotenv

        load_dotenv()
        mongo_uri = f"mongodb://{os.getenv('MONGO_DB_USERNAME')}:{os.getenv('MONGO_DB_PASSWORD')}@mongodb:27017/"
        _mongo = MongoClient(mongo_uri)

    return _mongo.database
