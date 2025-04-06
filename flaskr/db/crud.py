from datetime import datetime
from pymongo.collection import ReturnDocument

from flaskr.db.database import get_db
from flaskr.db.models import User, UserCreate, UserUpdate
from flaskr.utils import PasswordHasher, DataProjection


def activate_user(pre_created: dict, user_create: UserCreate, db=get_db()):
    """
    Activate a pre-created user record by updating it with the registration details.
    
    Steps:
    - Update the record with credentials from user_create (username, first_name, last_name, password_hash, major, etc.)
    - Mark is_active as True and set an activation timestamp.
    """
    update_data = {
        "username": user_create.username,
        "first_name": user_create.first_name,
        "last_name": user_create.last_name,
        "password_hash": user_create.password_hash,  # Already hashed in registration endpoint.
        "major": user_create.major,
        "is_active": True,
        "activated_at": datetime.now(),
        "last_login": datetime.fromtimestamp(0),
    }
    return db.users.find_one_and_update(
        {"_id": pre_created["_id"]},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )

def get_precreated_user(email: str):
    """Fetch a pre-created user by email (that is still inactive)."""
    db = get_db()
    return db.users.find_one({"email": email, "is_active": False})

def create_precreated_user(email: str, plain_license: str):
    db = get_db()
    license_hash = PasswordHasher.hash_password(plain_license) 
    user_document = {
        "email": email,
        "license_hash": license_hash,
        "is_active": False
    }
    result = db.users.insert_one(user_document)
    return result.inserted_id

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
    user = db.users.find_one({"username": username}, projection=DataProjection.user)
    if user and "_id" in user:
        user["_id"] = str(user["_id"])  # Convert ObjectId to string
    return user


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
