import os
from pymongo import MongoClient

# from flask import current_app

_mongo = None


def init_db():
    db = get_db()
    db.users.create_index("username", unique=True)
    db.users.create_index("email", unique=True)


def get_db():
    global _mongo
    if not _mongo:
        # from dotenv import load_dotenv

        # load_dotenv()
        mongo_uri = f"mongodb://{os.getenv('MONGO_DB_USERNAME')}:{os.getenv('MONGO_DB_PASSWORD')}@mongodb:27017/"
        print(mongo_uri)
        _mongo = MongoClient(mongo_uri)
        print("MongoDB connected")
        print(_mongo)
        print(_mongo.database)

    return _mongo.database
