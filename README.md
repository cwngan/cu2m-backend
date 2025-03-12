# CU2M Backend

# Prerequisites
- Python with pip install

# Environment Setup
1. Setup a virtual environment.
```bash
python3 -m venv .venv
```

2. Activate the virtual environment.
```bash
. .venv/bin/activate
```

3. Install required python packages.
```bash
python3 -m pip install -r requirements.txt
```

4. Start developing. Start the Flask server in debug mode with the following command.
```bash
flask --app flaskr run --debug
```

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

# Running with Docker
(To be implemented)