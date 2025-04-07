import csv
import sys
from flaskr.db.crud import create_precreated_user
from flaskr.utils import PasswordHasher


def batch_pre_create(csv_filepath):
    with open(csv_filepath, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            email = row["email"]
            plain_license = row["license_key"]
            license_hash = PasswordHasher.hash_password(plain_license)
            # Create a pre-created user record with inactive status.
            create_precreated_user(
                email=email, license_hash=license_hash, is_active=False
            )
            print(f"Pre-created user for: {email}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python batch_pre_create.py <csv_file>")
    batch_pre_create(sys.argv[1])
