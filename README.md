# CU2M Backend

# Prerequisites
- Python 3.12

# Environment Setup (Flask Server Only)
1. Setup a virtual environment.
```bash
python3 -m venv .venv
```

2. Activate the virtual environment.
```bash
. .venv/bin/activate
```

3. Install poetry.
```bash
pip install poetry
```

4. Install required python packages.
```bash
poetry install
```

5. Start developing. Start the Flask server in debug mode with the following command.
```bash
flask --app flaskr run --debug
```

6. To install more packages do the following.
```bash
poetry add <package-name>
```

# Environment Setup (With Database)
1. Download Docker and Docker Compose.
2. Use the following command for (re)building and running the docker container with watching. With watching, you can edit the source code and docker will try to reflect those changes as soon as possible.
```bash
docker compose --profile dev up --build --watch
```
3. Use the following command to start the server with watching.
```bash
docker compose --profile dev up --watch
```
4. You may want to run it in detach mode. Type the following command to do so (doesn't support watch).
```bash
docker compose --profile dev up -d
```
5. Use the following command for deploying in production environment.
```bash
docker compose --profile prod up
```

# Testing Procedure
1. Ensure you have `pytest`.
2. Use the following command to start testing with `pytest` (or you can just run with `./run_test.sh`).
```bash
MONGO_DB_USERNAME=tmp MONGO_DB_PASSWORD=tmp MONGO_DB_HOST=localhost MONGO_DB_PORT=27017 COURSE_DATA_FILENAME=courses_test.json pytest --show-capture=stderr
```
3. To run a specific test file, just mention test file path.
4. To run a specific test name, just add `-k` flag with the test function name
5. To increase the logger verbosity, add the environment variable `LOGGING_LEVEL=DEBUG`.

# Development Conventions
1. Use `black` for code formatting. Use the following command to format your code. You can also setup auto formatting in Visual Studio Code (install "Black Formatter" from Microsoft).
```bash
black .
```
2. Use `ruff` for code linting. Use the following command to lint your code. You can also setup auto linting in Visual Studio Code (install "Ruff" from Astral Software).
```bash
ruff check
```
3. Fix your errors linted by linter automatically with the following command. Note that some errors have to be fixed manually.
```bash
ruff check --fix
```
4. For variable naming conventions (quoted from [here](https://peps.python.org/pep-0008/#function-and-variable-names)):
- Class names should be in `PascalCase`.
- Function and variable names should be in `snake_case`.
- Constants names should be written in all capital letters with underscores separating words.
5. Remember to add tests to your newly developed API endpoint using `pytest`.
