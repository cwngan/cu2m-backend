from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from flask import session

from flaskr.api.respmodels import ResponseModel
from flaskr.db.user import get_user_by_username

P = ParamSpec("P")
R = TypeVar("R")


def auth_guard(func: Callable[P, R]):
    """
    Decorator to check if the user is logged in before executing the route function.

    use "user" in the function parameters to access the user object.
    """
    # Check if the function has a parameter named "user"
    # If it does, we will pass the user object to that parameter
    has_user = "user" in func.__annotations__

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs):
        username = session.get("username")
        user = get_user_by_username(username=username) if username else None
        if not user:
            return (
                ResponseModel(status="ERROR", error="Unauthorized").model_dump(),
                401,
            )
        if has_user:
            kwargs["user"] = user
        return func(*args, **kwargs)

    return wrapper
