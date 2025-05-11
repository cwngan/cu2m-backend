from base64 import b64encode

from flaskr import utils
from flaskr.db.models import UserCreate


def test_license_key_generator():
    TEST_EMAIL = "test@test.test"
    key_hash, key = utils.KeyGenerator.generate_new_key()
    assert key_hash is not None
    assert key is not None
    assert key_hash != key

    user = UserCreate(
        username=".",
        first_name=".",
        last_name=".",
        password=".",
        major=".",
        email=TEST_EMAIL,
        license_key=key,
    )

    assert utils.KeyGenerator.verify_key(user.license_key, key_hash) is True
    assert (
        utils.KeyGenerator.verify_key(
            user.license_key, "wrong_hash." + key_hash.split(".")[1]
        )
        is False
    )
    assert (
        utils.KeyGenerator.verify_key(
            user.license_key, key_hash.split(".")[0] + "." + b"wrong_salt".hex()
        )
        is False
    )
    user.license_key = "wrong_key"
    assert (
        utils.KeyGenerator.verify_key(user.license_key, key_hash) is False
    )  # wrong license key

    user.license_key = "!@#$%^&*()ADKMW31';]"
    assert (
        utils.KeyGenerator.verify_key(user.license_key, "asdaksdwqeqwe") is False
    )  # garbage


def test_password_hasher():
    TEST_PASSWORD = "test_password"
    password_hash = utils.PasswordHasher.hash_password(TEST_PASSWORD)
    assert password_hash is not None
    assert password_hash != TEST_PASSWORD
    assert utils.PasswordHasher.verify_password(password_hash, TEST_PASSWORD) is True
    assert (
        utils.PasswordHasher.verify_password(password_hash, "wrong_password") is False
    )
    assert (
        utils.PasswordHasher.verify_password("123k12op3123qk123", "asdl120123") is False
    )  # garbage
