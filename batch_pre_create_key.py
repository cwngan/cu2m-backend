from flaskr.db.crud import create_precreated_user


def create_precreated_users(input_path: str, out_path: str = "new_users_pre.txt"):
    with open(input_path, "r") as file:
        lines = file.readlines()

    with open(out_path, "a") as output_file:
        for line in lines:
            email = line.strip()
            try:
                license_key, _user = create_precreated_user(email)
                output_file.write(f"{email},{license_key}\n")
            except Exception as e:
                print(f"Error creating user for {email}: {e}")
                continue


if __name__ == "__main__":
    create_precreated_users("new_users.txt")
