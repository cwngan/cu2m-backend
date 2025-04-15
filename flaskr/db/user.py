from datetime import datetime, timezone

from pymongo.collection import ReturnDocument

from flaskr.db.database import get_db
from flaskr.db.models import PreUser, ResetToken, User, UserCreate, UserUpdate
from flaskr.utils import KeyGenerator, PasswordHasher


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
        {"$set": user.model_dump(exclude_none=True, exclude={"id"})},
        return_document=ReturnDocument.AFTER,
    )

    return User.model_validate(doc) if doc else None


def get_precreated_user(email: str):
    """Fetch a pre-created user by email (that is still inactive)."""
    userdb = get_db().users
    doc = userdb.find_one(
        {"email": email, "activated_at": datetime.fromtimestamp(0, timezone.utc)}
    )
    return PreUser.model_validate(doc) if doc else None


def create_precreated_user(email: str):
    """
    Create a pre-created user record with a license key.
    """
    userdb = get_db().users
    license_key_hash, license_key = KeyGenerator.generate_new_key()
    preuser = PreUser(
        email=email,
        license_key_hash=license_key_hash,
    )
    preuser.id = userdb.insert_one(preuser.model_dump(exclude_none=True)).inserted_id
    return license_key, preuser


def get_user_by_username(username: str):
    """
    Fetch a user by username.

    Note: Remember to parse with `UserRead` model to avoid exposing sensitive data.
    """
    userdb = get_db().users
    doc = userdb.find_one({"username": username})
    return User.model_validate(doc) if doc else None


def get_user_by_email(email: str):
    """
    Fetch a user by email.

    Note: Remember to parse with `UserRead` model to avoid exposing sensitive data.
    """
    userdb = get_db().users
    doc = userdb.find_one(
        {
            "email": email,
            "activated_at": {"$ne": datetime.fromtimestamp(0, timezone.utc)},
        }
    )
    return User.model_validate(doc) if doc else None


def update_user(username: str, user_update: UserUpdate):
    """
    Update a user's details.
    """
    userdb = get_db().users
    data = user_update.model_dump(exclude_none=True, exclude={"password"})
    if user_update.password:
        data["password_hash"] = PasswordHasher.hash_password(user_update.password)

    doc = userdb.find_one_and_update(
        {"username": username},
        {"$set": data},
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


def create_reset_token(email: str):
    """
    Create a forgot password token for the user.
    """
    user = get_user_by_email(email)
    if not user:
        return None, None

    tokendb = get_db().tokens
    key_hash, key = KeyGenerator.generate_new_key()

    token = ResetToken(
        token_hash=key_hash,
        username=user.username,
        expires_at=datetime.fromtimestamp(
            datetime.now().timestamp() + ResetToken.TTL, timezone.utc
        ),
    )

    tokendb.update_one(
        {"username": user.username},
        {"$set": token.model_dump(exclude_none=True)},
        upsert=True,
    )

    return key, user


def get_reset_token(username: str):
    """
    Get forgot password tokens for the user.
    """
    tokendb = get_db().tokens
    doc = tokendb.find_one({"username": username})
    if not doc:
        return None
    token = ResetToken.model_validate(doc)
    return token if token.is_valid() else None
