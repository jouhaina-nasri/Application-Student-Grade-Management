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

notes_bp = Blueprint("notes", __name__)


# ------------------------------------------------
# Show notes
# ------------------------------------------------
@notes_bp.route("/note")
@login_required()
def note_list():
    role = session.get("Role")
    user_id = session.get("user_id")

    conn = get_connection()
    cur = conn.cursor()

    # Teacher / admin / monitor → see all notes
    if role != "etudiant":
        cur.execute("SELECT * FROM note")
        notes = cur.fetchall()
        cur.close()
        conn.close()

        # If professor → editable notes page
        if role == "prof":
            return render_template("note.html", note=notes, user=role)
        # Admin / monitor → read-only page
        return render_template("affichenote.html", note=notes, user=role)

    # Student → see only own notes
    cur.execute("SELECT * FROM note WHERE idetudiant = %s", (user_id,))
    notes = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("affichenote.html", note=notes, user=role)


# ------------------------------------------------
# Insert note
# ------------------------------------------------
@notes_bp.route("/insertn", methods=["POST"])
@login_required("prof")
def insert_note():
    idnote = request.form.get("idnote")
    idetudiant = request.form.get("idetudiant")
    refmatiere = request.form.get("refmatiere")
    note_value = request.form.get("note")
    idprof = session.get("user_id")

    conn = get_connection()
    cur = conn.cursor()

    # Check if note ID already exists
    cur.execute("SELECT 1 FROM note WHERE idnote = %s", (idnote,))
    if cur.fetchone():
        flash("Note already exists.")
        cur.close()
        conn.close()
        return redirect(url_for("notes.note_list"))

    # Check if student exists
    cur.execute("SELECT 1 FROM etudiant WHERE idetudiant = %s", (idetudiant,))
    if not cur.fetchone():
        flash("Student does not exist.")
        cur.close()
        conn.close()
        return redirect(url_for("notes.note_list"))

    # Check if subject exists
    cur.execute("SELECT 1 FROM matiere WHERE refmatiere = %s", (refmatiere,))
    if not cur.fetchone():
        flash("Subject does not exist.")
        cur.close()
        conn.close()
        return redirect(url_for("notes.note_list"))

    # Insert note
    cur.execute(
        """
        INSERT INTO note (idnote, idetudiant, refmatiere, note, idprof)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (idnote, idetudiant, refmatiere, note_value, idprof),
    )
    conn.commit()
    cur.close()
    conn.close()

    flash("Note added successfully.")
    return redirect(url_for("notes.note_list"))


# ------------------------------------------------
# Update note
# ------------------------------------------------
@notes_bp.route("/updaten", methods=["POST"])
@login_required("prof")
def update_note():
    idnote = request.form.get("idnote")
    idetudiant = request.form.get("idetudiant")
    refmatiere = request.form.get("refmatiere")
    note_value = request.form.get("note")

    conn = get_connection()
    cur = conn.cursor()

    # Check if student exists and is active
    cur.execute(
        """
        SELECT 1 FROM user
        WHERE id = %s AND actif = 1 AND Role = 'etudiant'
        """,
        (idetudiant,),
    )
    if not cur.fetchone():
        flash("Student does not exist or is not active.")
        cur.close()
        conn.close()
        return redirect(url_for("notes.note_list"))

    # Check if subject exists
    cur.execute("SELECT 1 FROM matiere WHERE refmatiere = %s", (refmatiere,))
    if not cur.fetchone():
        flash("Subject does not exist.")
        cur.close()
        conn.close()
        return redirect(url_for("notes.note_list"))

    # Update note
    cur.execute(
        """
        UPDATE note
        SET note = %s, idetudiant = %s, refmatiere = %s
        WHERE idnote = %s
        """,
        (note_value, idetudiant, refmatiere, idnote),
    )
    conn.commit()
    cur.close()
    conn.close()

    flash("Note updated successfully.")
    return redirect(url_for("notes.note_list"))


# ------------------------------------------------
# Delete note
# ------------------------------------------------
@notes_bp.route("/deleten/<string:idnote>", methods=["GET"])
@login_required("prof")
def delete_note(idnote):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM note WHERE idnote = %s", (idnote,))
    conn.commit()
    cur.close()
    conn.close()

    flash("Note deleted successfully.")
    return redirect(url_for("notes.note_list"))


# ------------------------------------------------
# Calculate averages & bulletin
# ------------------------------------------------
@notes_bp.route("/calcul", methods=["POST"])
@login_required()
def calculate_results():
    idetudiant = request.form.get("id")

    conn = get_connection()
    cur = conn.cursor()

    # Check if student has any notes
    cur.execute("SELECT 1 FROM note WHERE idetudiant = %s", (idetudiant,))
    if not cur.fetchone():
        flash("This student has no notes.")
        cur.close()
        conn.close()
        return redirect(url_for("notes.note_list"))

    # Check if bulletin already exists
    cur.execute(
        "SELECT 1 FROM bulltin WHERE id_etudiant = %s",
        (idetudiant,),
    )
    if cur.fetchone():
        flash("This student already has a calculated average.")
        cur.close()
        conn.close()
        return redirect(url_for("notes.note_list"))

    # Insert per-module averages into bulltin
    cur.execute(
        """
        INSERT INTO bulltin (id_etudiant, nom_module, coefficient, moyenne)
        SELECT
            note.idetudiant,
            module.nom_module,
            module.coefficient,
            SUM(note.note * matiere.coefficient) / SUM(matiere.coefficient) AS moyenne
        FROM matiere, note, module
        WHERE
            note.idetudiant = %s
            AND note.refmatiere = matiere.refmatiere
            AND matiere.refmodule = module.refmodule
        GROUP BY module.refmodule, note.idetudiant, module.nom_module, module.coefficient
        """,
        (idetudiant,),
    )

    # Insert global result into resultat
    cur.execute(
        """
        INSERT INTO resultat (idetudiant, moyenne)
        SELECT
            b.id_etudiant,
            SUM(b.moyenne * b.coefficient) / SUM(b.coefficient)
        FROM bulltin b
        WHERE b.id_etudiant = %s
        """,
        (idetudiant,),
    )

    conn.commit()
    cur.close()
    conn.close()

    flash("Results calculated successfully.")
    return redirect(url_for("notes.note_list"))


# ------------------------------------------------
# Show results / bulletin
# ------------------------------------------------
@notes_bp.route("/resultat")
@login_required()
def resultat():
    role = session.get("Role")
    user_id = session.get("user_id")

    conn = get_connection()
    cur = conn.cursor()

    # Student → show their bulletin and global average
    if role == "etudiant":
        cur.execute(
            "SELECT * FROM bulltin WHERE id_etudiant = %s",
            (user_id,),
        )
        rows = cur.fetchall()

        total = None
        moyenne = None

        if rows:
            cur.execute(
                "SELECT SUM(moyenne) FROM bulltin WHERE id_etudiant = %s",
                (user_id,),
            )
            total = cur.fetchone()

            cur.execute(
                "SELECT moyenne FROM resultat WHERE idetudiant = %s",
                (user_id,),
            )
            moyenne = cur.fetchone()

        cur.close()
        conn.close()
        return render_template(
            "bulltin.html",
            resultat=rows,
            moyenne=moyenne,
            total=total,
            user=role,
        )

    # Other roles → see all results
    cur.execute("SELECT * FROM resultat")
    results = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("resultat.html", resultat=results, user=role)


# ------------------------------------------------
# Delete result (global)
# ------------------------------------------------
@notes_bp.route("/deleteresult/<string:student_id>", methods=["GET"])
@login_required()
def delete_result(student_id):
    conn = get_connection()
    cur = conn.cursor()

    # delete from resultat
    cur.execute("DELETE FROM resultat WHERE idetudiant = %s", (student_id,))
    conn.commit()

    cur.close()
    conn.close()

    flash("Result deleted successfully.")
    return redirect(url_for("notes.resultat"))
