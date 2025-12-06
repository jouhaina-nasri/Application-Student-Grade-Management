from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from passlib.hash import sha256_crypt

from .db import get_connection
from .decorators import login_required

auth_bp = Blueprint("auth", __name__)


# -------------------------
# Login
# -------------------------
@auth_bp.route("/login", methods=["GET"])
def login():
    """Show login page."""
    return render_template("login.html")


@auth_bp.route("/login", methods=["POST"])
def login_post():
    """Handle login form submission."""
    email = request.form.get("email")
    password = request.form.get("password")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nom, email, motdepasse, Role, actif FROM user WHERE email = %s",
        (email,),
    )
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user:
        flash("Incorrect email or password.")
        return redirect(url_for("auth.login"))

    user_id, name, email_db, hashed_password, role, active = user

    # Verify password
    if not sha256_crypt.verify(password, hashed_password):
        flash("Incorrect email or password.")
        return redirect(url_for("auth.login"))

    # Check if account is active
    if active is not None and active == 0:
        flash("Your account is blocked. Please contact the administrator.")
        return redirect(url_for("auth.login"))

    # Save user info in session
    session["user_id"] = user_id
    session["user"] = name
    session["Role"] = role

    flash("You are now logged in.")
    return redirect(url_for("auth.profile"))


# -------------------------
# Register
# -------------------------
@auth_bp.route("/register", methods=["GET"])
def register():
    """Show registration page."""
    return render_template("register.html")  


@auth_bp.route("/register", methods=["POST"])
def register_post():
    """Handle registration form submission."""
    user_id = request.form.get("id")
    name = request.form.get("uname")
    email = request.form.get("uemail")
    raw_password = request.form.get("upassword")
    role = request.form.get("Role")

    hashed_password = sha256_crypt.encrypt(str(raw_password))

    conn = get_connection()
    cur = conn.cursor()

    # Check if user or email already exists
    cur.execute(
        "SELECT id FROM user WHERE id = %s OR email = %s",
        (user_id, email),
    )
    if cur.fetchone():
        flash("User already exists.")
        cur.close()
        conn.close()
        return render_template("register.html")

    # Insert into user table
    cur.execute(
        """
        INSERT INTO user (id, nom, email, motdepasse, Role, actif)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (user_id, name, email, hashed_password, role, 1),
    )

    # Insert into role-specific table
    if role == "admin":
        cur.execute("INSERT INTO admin (ID_admin) VALUES (%s)", (user_id,))
    elif role == "moniteur":
        cur.execute("INSERT INTO moniteur (id_moniteur) VALUES (%s)", (user_id,))
    elif role == "prof":
        cur.execute("INSERT INTO prof (idprof) VALUES (%s)", (user_id,))
    elif role == "etudiant":
        cur.execute("INSERT INTO etudiant (idetudiant) VALUES (%s)", (user_id,))

    conn.commit()
    cur.close()
    conn.close()

    flash("Account created successfully. You can now log in.")
    return redirect(url_for("auth.login"))


# -------------------------
# Profile
# -------------------------
@auth_bp.route("/profile")
@login_required()
def profile():
    """User profile page."""
    return render_template("profile.html", user=session.get("Role"))


# -------------------------
# Logout
# -------------------------
@auth_bp.route("/logout")
def logout():
    """Log the user out."""
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("auth.login"))
