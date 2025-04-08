from datetime import datetime, timezone

from flaskr.db import user as pkg
from flaskr.db.models import PreUser, UserCreate, UserUpdate
from flaskr.utils import LicenseKeyGenerator
from tests.utils import random_user


def test_precreated_user():
    from flaskr.db.database import get_db

    userdb = get_db().users
    TEST_EMAIL = "test@test.test"

    # verify data was placed correctly
    license_key, preuser = pkg.create_precreated_user(TEST_EMAIL)
    assert preuser is not None
    assert preuser.email == TEST_EMAIL
    assert preuser.activated_at == datetime.fromtimestamp(0, timezone.utc)
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
        LicenseKeyGenerator.verify_key(user_create, pkg_preuser.license_key_hash)
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
    assert res_user.username == TEST_USER.username
    assert res_user.first_name == TEST_USER.first_name
    assert res_user.last_name == TEST_USER.last_name
    assert res_user.major == TEST_USER.major
    assert res_user.email == TEST_USER.email
    assert res_user.password_hash is not None
    assert res_user.license_key_hash == preuser.license_key_hash
    assert res_user.activated_at != datetime.fromtimestamp(0)
    assert res_user.last_login is not None
    assert res_user.id == preuser.id

    assert pkg.get_precreated_user(TEST_USER.email) is None
    assert userdb.count_documents({}) == 1

    user = pkg.get_user(TEST_USER.username)
    assert user is not None
    assert user == res_user

    from bson import ObjectId

    preuser.id = ObjectId()
    res_user.id = preuser.id
    assert pkg.activate_user(preuser, TEST_USER) is None
    assert userdb.count_documents({}) == 1

    assert pkg.get_user("wrong_username") is None

    userdb.delete_many({})
    assert userdb.count_documents({}) == 0
    assert pkg.get_user(TEST_USER.username) is None


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

    original_user = pkg.get_user(users[0])
    assert original_user is not None

    res = pkg.update_user(original_user.username, UserUpdate(username="new_username"))
    assert res is not None
    assert res.username == "new_username"
    assert res.username != original_user.username
    assert pkg.get_user(original_user.username) is None
    assert pkg.get_user(res.username) == res
    original_user.username = res.username
    assert res == original_user

    original_user = pkg.get_user(users[1])
    assert original_user is not None
    tm = datetime.now(timezone.utc)
    tm = tm.replace(
        microsecond=(tm.microsecond // 1000) * 1000
    )  # trunk to milliseconds because of MongoDB precision
    res = pkg.update_user(original_user.username, UserUpdate(last_login=tm))
    assert res is not None
    assert pkg.get_user(original_user.username) == res
    assert res.last_login == tm
    assert res.last_login != original_user.last_login
    original_user.last_login = res.last_login
    assert res == original_user

    original_user = pkg.get_user(users[2])
    assert original_user is not None
    res = pkg.update_user(
        original_user.username, UserUpdate(password="new_password", major="new_major")
    )
    assert res is not None
    assert pkg.get_user(original_user.username) == res
    assert res.password_hash != original_user.password_hash
    assert res.major != original_user.major
    assert res.major == "new_major"
    original_user.password_hash = res.password_hash
    original_user.major = res.major
    assert res == original_user

    assert pkg.delete_user(original_user.username) is not None
    assert pkg.get_user(original_user.username) is None
    assert userdb.count_documents({}) == N - 1
    assert pkg.delete_user(original_user.username) is None

    for user in users[3:]:
        assert pkg.delete_user(user) is not None
        assert pkg.get_user(user) is None

    assert userdb.count_documents({}) == 2
