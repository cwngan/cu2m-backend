from datetime import datetime

from pymongo.collection import ReturnDocument

from flaskr.db.database import get_db
from flaskr.db.models import PreUser, User, UserCreate, UserUpdate
from flaskr.utils import LicenseKeyGenerator, PasswordHasher


def activate_user(pre_user: PreUser, user_create: UserCreate):
    """
    Activate a pre-created user record by updating it with the registration details.

    Steps:
    - Update the record with credentials from user_create (username, first_name, last_name, password, major, etc.)
    - Mark is_active as True and set an activation timestamp.
    """

    user = User(
        _id=pre_user.id,
        email=pre_user.email,
        username=user_create.username,
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        major=user_create.major,
        password_hash=PasswordHasher.hash_password(user_create.password),
        license_key_hash=pre_user.license_key_hash,
        last_login=datetime.now(),
        activated_at=datetime.now(),
    )

    userdb = get_db().users
    doc = userdb.find_one_and_update(
        {"_id": user.id},
        {"$set": user.model_dump(exclude_none=True)},
        return_document=ReturnDocument.AFTER,
    )

    return User.model_validate(doc) if doc else None


def get_precreated_user(email: str):
    """Fetch a pre-created user by email (that is still inactive)."""
    userdb = get_db().users
    doc = userdb.find_one({"email": email, "activated_at": datetime.fromtimestamp(0)})
    return PreUser.model_validate(doc) if doc else None


def create_precreated_user(email: str):
    """
    Create a pre-created user record with a license key.
    """
    userdb = get_db().users
    license_key_hash, license_key = LicenseKeyGenerator.generate_new_key(email)
    preuser = PreUser(
        email=email,
        license_key_hash=license_key_hash,
    )
    preuser.id = userdb.insert_one(preuser.model_dump(exclude_none=True)).inserted_id
    return license_key, preuser


def read_user(username: str):
    """
    Fetch a user by username.

    Note: Remember to parse with `UserRead` model to avoid exposing sensitive data.
    """
    userdb = get_db().users
    doc = userdb.find_one({"username": username})
    return User.model_validate(doc) if doc else None


def update_user(username: str, user_update: UserUpdate):
    """
    Update a user's details.
    """
    userdb = get_db().users
    doc = userdb.find_one_and_update(
        {"username": username},
        {"$set": user_update.__dict__},
        return_document=ReturnDocument.AFTER,
    )
    return User.model_validate(doc) if doc else None


def delete_user(username: str):
    """
    Delete a user by username.
    """

    userdb = get_db().users
    user = userdb.find_one({"username": username})
    if user:
        doc = userdb.find_one_and_delete(user)
        return User.model_validate(doc) if doc else None
    return None
