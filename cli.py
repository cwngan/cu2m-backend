import os
import sys

if len(sys.argv) < 2:
    print("Usage: python cli.py [dev|prod]")
    sys.exit(1)
args = sys.argv[1]
assert args is None or args == "dev" or args == "prod"

while True:
    line = input("To create a new user, type 'create [email]', or 'exit' to quit: ")
    if line == "exit":
        break
    elif line.startswith("create "):
        email = line.split(" ")[1]
        print(f"Creating user with email: {email}")
        data = {"email": email}
        os.system(
            " ".join(
                [
                    "docker",
                    "exec",
                    "-it",
                    f"cu2m-cu2m-backend{'-dev' if args == 'dev' else ''}-1",
                    "python3",
                    "-c",
                    "\"import requests; print(requests.post('http://127.0.0.1:5000/api/user/license', json={data}).json())\"".format(
                        data=data.__str__()
                    ),
                ]
            )
        )
    else:
        print("Invalid command. Please try again.")
