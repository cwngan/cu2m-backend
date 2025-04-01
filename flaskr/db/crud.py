from datetime import datetime
from pymongo.collection import ReturnDocument

from flaskr.db.database import get_db
from flaskr.db.models import User, UserCreate, UserUpdate
from flaskr.utils import PasswordHasher, DataProjection


def create_user(user_create: UserCreate, license_key_hash: str, db=get_db()):
    if read_user(user_create.username):
        return None
    password_hash = PasswordHasher.hash_password(user_create.password)
    new_user = User(
        email=user_create.email,
        first_name=user_create.first_name,
        last_login=datetime.fromtimestamp(0),
        last_name=user_create.last_name,
        license_key_hash=license_key_hash,
        major=user_create.major,
        password_hash=password_hash,
        username=user_create.username,
    )
    inserted_id = db.users.insert_one(new_user.__dict__).inserted_id
    return db.users.find_one({"_id": inserted_id}, projection=DataProjection.user)


def read_user(username: str, db=get_db()):
    return db.users.find_one({"username": username}, projection=DataProjection.user)


def read_user_full(username: str, db=get_db()):
    return db.users.find_one({"username": username})


def update_user(username: str, user_update: UserUpdate, db=get_db()) -> User | None:
    return db.users.find_one_and_update(
        {"username": username},
        {"$set": user_update.__dict__},
        projection=DataProjection.user,
        return_document=ReturnDocument.AFTER,
    )


def delete_user(username: str, db=get_db()):
    user = db.users.find_one({"username": username})
    if user:
        db.users.find_one_and_delete(user, projection=DataProjection.user)
        return user
    return None
