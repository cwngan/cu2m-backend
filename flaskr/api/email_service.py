import os
import smtplib
import ssl
from urllib.parse import urlencode

from flaskr.db.models import User


def send_reset_password_token(user: User, token: str):
    TITLE = "CU2M Password Reset"
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_SERVER_PORT = os.getenv("SMTP_SERVER_PORT")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    SMTP_EMAIL = os.getenv("SMTP_EMAIL")
    FRONTEND_URL = os.getenv("FRONTEND_URL")

    assert SMTP_SERVER is not None
    assert SMTP_SERVER_PORT is not None
    assert SMTP_PASSWORD is not None
    assert SMTP_EMAIL is not None
    assert FRONTEND_URL is not None

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(
        SMTP_SERVER, int(SMTP_SERVER_PORT), context=context
    ) as server:
        server.ehlo()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(
            SMTP_EMAIL,
            user.email,
            "Subject: {}\n\n{}".format(
                TITLE,
                f"Click the following link to reset your CU2M account password: "
                f"{FRONTEND_URL}/reset-password?{urlencode({'username': user.username, 'token': token})}",
            ),
        )
        server.quit()
