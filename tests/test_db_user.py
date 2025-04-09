from datetime import datetime, timezone

from flaskr.db import user as pkg
from flaskr.db.models import PreUser, ResetToken, UserCreate, UserUpdate
from flaskr.utils import KeyGenerator
from tests.utils import random_user


def test_precreated_user():
    from flaskr.db.database import get_db

    userdb = get_db().users
    TEST_EMAIL = "test@test.test"

    # verify data was placed correctly
    license_key, preuser = pkg.create_precreated_user(TEST_EMAIL)
    assert preuser is not None
    assert preuser.email == TEST_EMAIL
    assert preuser.activated_at.timestamp() == 0
    assert preuser.license_key_hash is not None
    assert preuser.id is not None

    assert userdb.count_documents({}) == 1

    doc = userdb.find_one({"email": TEST_EMAIL})
    assert doc is not None
    doc_preuser = PreUser.model_validate(doc)
    assert doc_preuser == preuser

    pkg_preuser = pkg.get_precreated_user(TEST_EMAIL)
    assert pkg_preuser is not None
    assert pkg_preuser == preuser

    # verify license key and hash were placed correctly
    user_create = UserCreate(
        username=".",
        first_name=".",
        last_name=".",
        password=".",
        major=".",
        email=TEST_EMAIL,
        license_key=license_key,
    )
    assert (
        KeyGenerator.verify_key(user_create.license_key, pkg_preuser.license_key_hash)
        is True
    )

    userdb.delete_many({})
    assert userdb.count_documents({}) == 0
    assert pkg.get_precreated_user(TEST_EMAIL) is None


def test_activate_get_user():
    from flaskr.db.database import get_db

    userdb = get_db().users
    TEST_USER = UserCreate(
        email="test@test.test",
        username="test",
        first_name="johnny",
        last_name="test",
        password="password",
        major="test",
        license_key="test",
    )

    _, preuser = pkg.create_precreated_user(TEST_USER.email)
    assert preuser is not None
    assert pkg.get_precreated_user(TEST_USER.email) == preuser
    assert userdb.count_documents({}) == 1

    res_user = pkg.activate_user(preuser, TEST_USER)
    assert res_user is not None
    assert (
        UserCreate.model_validate(
            {
                **res_user.model_dump(),
                "password": TEST_USER.password,
                "license_key": TEST_USER.license_key,
            }
        )
        == TEST_USER
    )
    assert res_user.password_hash is not None
    assert res_user.license_key_hash == preuser.license_key_hash
    # assuming test wont take more than 3 seconds
    assert datetime.now().timestamp() - res_user.activated_at.timestamp() < 3
    assert res_user.last_login is not None
    assert res_user.id == preuser.id

    assert pkg.get_precreated_user(TEST_USER.email) is None
    assert userdb.count_documents({}) == 1

    user = pkg.get_by_username(TEST_USER.username)
    assert user is not None
    assert user == res_user

    from bson import ObjectId

    preuser.id = ObjectId()
    res_user.id = preuser.id
    assert pkg.activate_user(preuser, TEST_USER) is None
    assert userdb.count_documents({}) == 1

    assert pkg.get_by_username("wrong_username") is None

    userdb.delete_many({})
    assert userdb.count_documents({}) == 0
    assert pkg.get_by_username(TEST_USER.username) is None


def test_update_delete_user():

    from flaskr.db.database import get_db

    userdb = get_db().users
    N = 10
    users: list[str] = []
    for i in range(N):
        user = random_user()
        users.append(user.username)
        userdb.insert_one(user.model_dump(exclude_none=True))
        assert userdb.count_documents({}) == i + 1

    original_user = pkg.get_by_username(users[0])
    assert original_user is not None

    res = pkg.update_user(original_user.username, UserUpdate(username="new_username"))
    assert res is not None
    assert res.username == "new_username"
    assert res.username != original_user.username
    assert pkg.get_by_username(original_user.username) is None
    assert pkg.get_by_username(res.username) == res
    original_user.username = res.username
    assert res == original_user

    original_user = pkg.get_by_username(users[1])
    assert original_user is not None
    tm = datetime.now(timezone.utc)
    tm = tm.replace(
        microsecond=(tm.microsecond // 1000) * 1000
    )  # trunk to milliseconds because of MongoDB precision
    res = pkg.update_user(original_user.username, UserUpdate(last_login=tm))
    assert res is not None
    assert pkg.get_by_username(original_user.username) == res
    assert res.last_login.timestamp() == tm.timestamp()
    assert res.last_login.timestamp() >= original_user.last_login.timestamp()
    original_user.last_login = res.last_login
    assert res == original_user

    original_user = pkg.get_by_username(users[2])
    assert original_user is not None
    res = pkg.update_user(
        original_user.username, UserUpdate(password="new_password", major="new_major")
    )
    assert res is not None
    assert pkg.get_by_username(original_user.username) == res
    assert res.password_hash != original_user.password_hash
    assert res.major != original_user.major
    assert res.major == "new_major"
    original_user.password_hash = res.password_hash
    original_user.major = res.major
    assert res == original_user

    assert pkg.delete_user(original_user.username) is not None
    assert pkg.get_by_username(original_user.username) is None
    assert userdb.count_documents({}) == N - 1
    assert pkg.delete_user(original_user.username) is None

    for user in users[3:]:
        assert pkg.delete_user(user) is not None
        assert pkg.get_by_username(user) is None

    assert userdb.count_documents({}) == 2


def test_reset_token():
    from flaskr.db.database import get_db

    userdb = get_db().users
    tokendb = get_db().tokens
    TEST_USER = random_user()
    TEST_USER.id = userdb.insert_one(
        TEST_USER.model_dump(exclude_none=True)
    ).inserted_id

    key, user = pkg.create_reset_token(TEST_USER.email)
    
    assert tokendb.count_documents({}) == 1
    assert user == TEST_USER
    assert key is not None

    token = pkg.get_reset_token(TEST_USER.username)
    assert token is not None
    assert token.username == TEST_USER.username
    assert KeyGenerator.verify_key(key, token.token_hash) is True
    assert token.expires_at.timestamp() > datetime.now().timestamp()
    assert token.expires_at.timestamp() <= datetime.now().timestamp() + ResetToken.TTL
    tokendb.update_one(
        {"_id": token.id},
        {"$set": {"expires_at": datetime.fromtimestamp(0, timezone.utc)}},
    )
    token = pkg.get_reset_token(TEST_USER.username)
    assert token is None

    assert pkg.get_reset_token("wrong_username") is None
    assert pkg.create_reset_token("wrong_email") == (None, None)

    
    key1, user1 = pkg.create_reset_token(TEST_USER.email)
    assert user1 == TEST_USER
    assert key1 is not None

    key2, user2 = pkg.create_reset_token(TEST_USER.email)
    assert user2 == TEST_USER
    assert key2 is not None
    assert key1 != key2
    assert tokendb.count_documents({}) == 1

    token = pkg.get_reset_token(TEST_USER.username)
    assert token is not None
    assert KeyGenerator.verify_key(key1, token.token_hash) is False
    assert KeyGenerator.verify_key(key2, token.token_hash) is True
