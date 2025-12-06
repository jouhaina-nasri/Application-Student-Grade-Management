from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)

from .db import get_connection
from .decorators import login_required

modules_bp = Blueprint("modules", __name__)


# ====================================================
# MODULES
# ====================================================

# ----------------------------------------
# List modules
# ----------------------------------------
@modules_bp.route("/module")
@login_required()
def module_list():
    role = session.get("Role")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM module")
    modules = cur.fetchall()
    cur.close()
    conn.close()

    # Admin / monitor → management page
    if role in ("admin", "moniteur"):
        return render_template("module.html", module=modules, user=role)

    # Other roles → read-only view
    return render_template("affichemodule.html", module=modules, user=role)


# ----------------------------------------
# Insert module
# ----------------------------------------
@modules_bp.route("/insertm", methods=["POST"])
@login_required()
def insert_module():
    # Only admin or monitor can insert
    role = session.get("Role")
    if role not in ("admin", "moniteur"):
        flash("You are not allowed to create modules.")
        return redirect(url_for("modules.module_list"))

    refmodule = request.form.get("refmodule")
    nom_module = request.form.get("nom_module")
    coeff = request.form.get("coeff")

    conn = get_connection()
    cur = conn.cursor()

    # Check if refmodule or name already exists
    cur.execute(
        "SELECT 1 FROM module WHERE refmodule = %s OR nom_module = %s",
        (refmodule, nom_module),
    )
    if cur.fetchone():
        flash("Module already exists or information is not valid.")
        cur.close()
        conn.close()
        return redirect(url_for("modules.module_list"))

    # Insert new module
    cur.execute(
        "INSERT INTO module (refmodule, nom_module, coefficient) VALUES (%s, %s, %s)",
        (refmodule, nom_module, coeff),
    )
    conn.commit()
    cur.close()
    conn.close()

    flash("Module added successfully.")
    return redirect(url_for("modules.module_list"))


# ----------------------------------------
# Update module
# ----------------------------------------
@modules_bp.route("/updatem", methods=["POST"])
@login_required()
def update_module():
    role = session.get("Role")
    if role not in ("admin", "moniteur"):
        flash("You are not allowed to update modules.")
        return redirect(url_for("modules.module_list"))

    refmodule = request.form.get("refmodule")
    nom_module = request.form.get("nom_module")
    coeff = request.form.get("coeff")

    conn = get_connection()
    cur = conn.cursor()

    # Get existing module
    cur.execute("SELECT refmodule, nom_module, coefficient FROM module WHERE refmodule = %s", (refmodule,))
    row = cur.fetchone()

    if not row:
        flash("Module not found.")
        cur.close()
        conn.close()
        return redirect(url_for("modules.module_list"))

    old_name = row[1]

    if nom_module != old_name:
        cur.execute(
            "SELECT 1 FROM module WHERE nom_module = %s AND refmodule <> %s",
            (nom_module, refmodule),
        )
        if cur.fetchone():
            flash("Another module already uses this name.")
            cur.close()
            conn.close()
            return redirect(url_for("modules.module_list"))

    # Update module
    cur.execute(
        "UPDATE module SET nom_module = %s, coefficient = %s WHERE refmodule = %s",
        (nom_module, coeff, refmodule),
    )
    conn.commit()
    cur.close()
    conn.close()

    flash("Module updated successfully.")
    return redirect(url_for("modules.module_list"))


# ----------------------------------------
# Delete module
# ----------------------------------------
@modules_bp.route("/deletem/<string:refmodule>", methods=["GET"])
@login_required()
def delete_module(refmodule):
    role = session.get("Role")
    if role not in ("admin", "moniteur"):
        flash("You are not allowed to delete modules.")
        return redirect(url_for("modules.module_list"))

    conn = get_connection()
    cur = conn.cursor()

    # Delete related subjects (matiere) first
    cur.execute("DELETE FROM matiere WHERE refmodule = %s", (refmodule,))
    # Then delete module
    cur.execute("DELETE FROM module WHERE refmodule = %s", (refmodule,))
    conn.commit()

    cur.close()
    conn.close()

    flash("Module and its subjects were deleted successfully.")
    return redirect(url_for("modules.module_list"))


# ====================================================
# SUBJECTS
# ====================================================

# ----------------------------------------
# List subjects
# ----------------------------------------
@modules_bp.route("/matiere")
@login_required()
def matiere_list():
    role = session.get("Role")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM matiere")
    matieres = cur.fetchall()
    cur.close()
    conn.close()

    if role in ("admin", "moniteur"):
        return render_template("matiere.html", matiere=matieres, user=role)

    return render_template("affichematiere.html", matiere=matieres, user=role)


# ----------------------------------------
# Insert subject
# ----------------------------------------
@modules_bp.route("/insertmat", methods=["POST"])
@login_required()
def insert_matiere():
    role = session.get("Role")
    if role not in ("admin", "moniteur"):
        flash("You are not allowed to create subjects.")
        return redirect(url_for("modules.matiere_list"))

    refmatiere = request.form.get("refmatiere")
    refmodule = request.form.get("refmodule")
    nom_matiere = request.form.get("nom_matiere")
    coefficient = request.form.get("coefficient")

    conn = get_connection()
    cur = conn.cursor()

    # Check if subject code or name already exists
    cur.execute(
        "SELECT 1 FROM matiere WHERE refmatiere = %s OR nom_matiere = %s",
        (refmatiere, nom_matiere),
    )
    if cur.fetchone():
        flash("Subject already exists or information is not valid.")
        cur.close()
        conn.close()
        return redirect(url_for("modules.matiere_list"))

    # Check if module exists
    cur.execute("SELECT 1 FROM module WHERE refmodule = %s", (refmodule,))
    if not cur.fetchone():
        flash("Module does not exist.")
        cur.close()
        conn.close()
        return redirect(url_for("modules.matiere_list"))

    # Insert subject
    cur.execute(
        """
        INSERT INTO matiere (refmatiere, refmodule, nom_matiere, coefficient)
        VALUES (%s, %s, %s, %s)
        """,
        (refmatiere, refmodule, nom_matiere, coefficient),
    )
    conn.commit()
    cur.close()
    conn.close()

    flash("Subject added successfully.")
    return redirect(url_for("modules.matiere_list"))


# ----------------------------------------
# Update subject
# ----------------------------------------
@modules_bp.route("/updatemat", methods=["POST"])
@login_required()
def update_matiere():
    role = session.get("Role")
    if role not in ("admin", "moniteur"):
        flash("You are not allowed to update subjects.")
        return redirect(url_for("modules.matiere_list"))

    refmatiere = request.form.get("refmatiere")
    refmodule = request.form.get("refmodule")
    nom_matiere = request.form.get("nom_matiere")
    coefficient = request.form.get("coefficient")

    conn = get_connection()
    cur = conn.cursor()

    # Get existing subject
    cur.execute(
        "SELECT refmatiere, refmodule, nom_matiere, coefficient FROM matiere WHERE refmatiere = %s",
        (refmatiere,),
    )
    row = cur.fetchone()

    if not row:
        flash("Subject not found.")
        cur.close()
        conn.close()
        return redirect(url_for("modules.matiere_list"))

    old_name = row[2]

    # If name changed → check if the new name is already used
    if nom_matiere != old_name:
        cur.execute(
            "SELECT 1 FROM matiere WHERE nom_matiere = %s AND refmatiere <> %s",
            (nom_matiere, refmatiere),
        )
        if cur.fetchone():
            flash("Another subject already uses this name.")
            cur.close()
            conn.close()
            return redirect(url_for("modules.matiere_list"))

        # Update both name and coefficient (like original logic)
        cur.execute(
            """
            UPDATE matiere
            SET nom_matiere = %s, coefficient = %s, refmodule = %s
            WHERE refmatiere = %s
            """,
            (nom_matiere, coefficient, refmodule, refmatiere),
        )
        conn.commit()
        cur.close()
        conn.close()

        flash("Subject updated successfully.")
        return redirect(url_for("modules.matiere_list"))

    # If name did not change → update only coefficient and module
    cur.execute(
        """
        UPDATE matiere
        SET coefficient = %s, refmodule = %s
        WHERE refmatiere = %s
        """,
        (coefficient, refmodule, refmatiere),
    )
    conn.commit()
    cur.close()
    conn.close()

    flash("Subject updated successfully.")
    return redirect(url_for("modules.matiere_list"))


# ----------------------------------------
# Delete subject
# ----------------------------------------
@modules_bp.route("/deletemat/<string:refmatiere>", methods=["GET"])
@login_required()
def delete_matiere(refmatiere):
    role = session.get("Role")
    if role not in ("admin", "moniteur"):
        flash("You are not allowed to delete subjects.")
        return redirect(url_for("modules.matiere_list"))

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM matiere WHERE refmatiere = %s", (refmatiere,))
    conn.commit()
    cur.close()
    conn.close()

    flash("Subject deleted successfully.")
    return redirect(url_for("modules.matiere_list"))
