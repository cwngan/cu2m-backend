
FROM python:3.12-alpine

ENV POETRY_VIRTUALENVS_CREATE=false

RUN pip install poetry

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install
COPY courses*.json .

CMD ["flask", "--app", "flaskr:create_app()", "run", "--debug", "--host=0.0.0.0"]