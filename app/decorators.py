from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(role=None):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("You must be logged in to access this page.")
                return redirect(url_for("auth.login"))
            if role and session.get("Role") != role:
                flash("Access denied.")
                return redirect(url_for("auth.profile"))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper
