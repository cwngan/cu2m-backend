import os
import smtplib
import ssl
from urllib.parse import quote_plus

from flaskr.db.models import User


def send_reset_password_token(user: User, token: str):
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_SERVER_PORT = os.getenv("SMTP_SERVER_PORT")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    SMTP_EMAIL = os.getenv("SMTP_EMAIL")
    RESET_EMAIL_CONTENT = os.getenv("RESET_EMAIL_CONTENT")

    assert SMTP_SERVER is not None
    assert SMTP_SERVER_PORT is not None
    assert SMTP_PASSWORD is not None
    assert SMTP_EMAIL is not None
    assert RESET_EMAIL_CONTENT is not None

    token = quote_plus(token)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(
        SMTP_SERVER, int(SMTP_SERVER_PORT), context=context
    ) as server:
        server.ehlo()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(
            SMTP_EMAIL,
            user.email,
            RESET_EMAIL_CONTENT.format(token=token, **user.model_dump()),
        )
        server.quit()
