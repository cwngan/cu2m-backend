from base64 import b64encode

from flaskr import utils
from flaskr.db.models import UserCreate


def test_license_key_generator():
    TEST_EMAIL = "test@test.test"
    key_hash, key = utils.LicenseKeyGenerator.generate_new_key(TEST_EMAIL)
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

    assert utils.LicenseKeyGenerator.verify_key(user, key_hash) is True
    assert (
        utils.LicenseKeyGenerator.verify_key(
            user, "wrong_hash." + key_hash.split(".")[1]
        )
        is False
    )
    assert (
        utils.LicenseKeyGenerator.verify_key(
            user, key_hash.split(".")[0] + "." + b"wrong_salt".hex()
        )
        is False
    )
    user.license_key = "wrong_key"
    assert (
        utils.LicenseKeyGenerator.verify_key(user, key_hash) is False
    )  # wrong license key


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
        utils.PasswordHasher.verify_password(
            f"16384$8$1${password_hash.split("$")[-2]}${b64encode(b"wronghash").decode('ascii')}",
            TEST_PASSWORD,
        )
        is False
    )  # wrong hash
    assert (
        utils.PasswordHasher.verify_password(
            f"16384$8$1${b64encode(b"wrong_salt").decode('ascii')}${password_hash.split('$')[-1]}",
            TEST_PASSWORD,
        )
        is False
    )  # wrong salt
