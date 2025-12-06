# app/users.py
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

users_bp = Blueprint("users", __name__)


# ------------------------------------------------
# List active users 
# ------------------------------------------------
@users_bp.route("/manage_user")
@login_required()
def manage_user():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM user WHERE id <> %s AND actif = 1",
        (session["user_id"],),
    )
    users = cur.fetchall()
    cur.close()
    conn.close()

    # If admin → show full user management page
    # Else      → show contact list page
    if session.get("Role") == "admin":
        return render_template("user.html", prof=users, user=session["Role"])
    else:
        return render_template("contactuser.html", prof=users, user=session["Role"])


# ------------------------------------------------
# List blocked users
# ------------------------------------------------
@users_bp.route("/bloque")
@login_required("admin")
def blocked_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE actif = 0")
    users = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("bloque.html", prof=users, user=session["Role"])


# ------------------------------------------------
# Create user
# ------------------------------------------------
@users_bp.route("/insert", methods=["POST"])
@login_required("admin")
def insert_user():
    user_id = request.form.get("id")
    name = request.form.get("name")
    email = request.form.get("email")
    raw_password = request.form.get("motdepasse")
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
        return redirect(url_for("users.manage_user"))

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
    else:  # student
        cur.execute("INSERT INTO etudiant (idetudiant) VALUES (%s)", (user_id,))

    conn.commit()
    cur.close()
    conn.close()

    flash("User created successfully.")
    return redirect(url_for("users.manage_user"))


# ------------------------------------------------
# Update user
# ------------------------------------------------
@users_bp.route("/update", methods=["POST"])
@login_required("admin")
def update_user():
    user_id = request.form.get("id")
    name = request.form.get("name")
    email = request.form.get("email")
    role = request.form.get("Role")

    conn = get_connection()
    cur = conn.cursor()

    # Check if email is used by another user
    cur.execute(
        "SELECT id FROM user WHERE email = %s AND id <> %s",
        (email, user_id),
    )
    if cur.fetchone():
        flash("This email is already used by another user.")
        cur.close()
        conn.close()
        return redirect(url_for("users.manage_user"))

    cur.execute(
        "UPDATE user SET nom = %s, email = %s, Role = %s WHERE id = %s",
        (name, email, role, user_id),
    )
    conn.commit()
    cur.close()
    conn.close()

    flash("User updated successfully.")
    return redirect(url_for("users.manage_user"))


# ------------------------------------------------
# Block user
# ------------------------------------------------
@users_bp.route("/block/<string:user_id>", methods=["GET"])
@login_required("admin")
def block_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE user SET actif = 0 WHERE id = %s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

    flash("User has been blocked.")
    return redirect(url_for("users.manage_user"))


# ------------------------------------------------
# Unblock user
# ------------------------------------------------
@users_bp.route("/unblock/<string:user_id>", methods=["GET"])
@login_required("admin")
def unblock_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE user SET actif = 1 WHERE id = %s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

    flash("User has been unblocked.")
    return redirect(url_for("users.blocked_users"))
