FROM python:3.12-alpine

RUN pip install gunicorn

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /app/flaskr
COPY flaskr .

WORKDIR /app
COPY req_fmt.json .
ENV PORT=8080
CMD ["gunicorn", "-w", "4", "flaskr:create_app()"]


