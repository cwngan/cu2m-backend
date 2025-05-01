from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from flask import session

from flaskr.api.respmodels import CoursePlanResponseModel
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
    # delete it from the annotations to avoid confusing flask_pydantic

    has_user = func.__annotations__.get("user") is not None
    if has_user:
        del func.__annotations__["user"]

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs):
        username = session.get("username")
        user = get_user_by_username(username=username) if username else None
        if not user:
            return (
                CoursePlanResponseModel(status="ERROR", error="Unauthorized"),
                401,
            )
        if has_user:
            kwargs["user"] = user
        return func(*args, **kwargs)

    return wrapper
