from flaskr.db.models import User


def send_reset_password_token(user: User, token: str):
    raise NotImplementedError("Email service not implemented yet.")
