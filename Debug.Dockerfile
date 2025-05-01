
FROM python:3.12-alpine

ENV POETRY_VIRTUALENVS_CREATE=false

RUN pip install poetry

WORKDIR /app
COPY courses*.json .
COPY pyproject.toml poetry.lock ./
RUN poetry install

ENV PORT=8080
CMD ["flask", "--app", "flaskr:create_app()", "run", "--debug"]