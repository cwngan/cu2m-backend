FROM python:3.12-alpine

ENV POETRY_VIRTUALENVS_CREATE=false

RUN pip install poetry

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install

WORKDIR /app/flaskr
COPY flaskr .

WORKDIR /app
COPY courses*.json .
ENV PORT=8080
CMD ["gunicorn", "-w", "4", "flaskr:create_app()"]
