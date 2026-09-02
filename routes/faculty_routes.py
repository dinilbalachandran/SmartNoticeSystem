from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

from database.database import (
    get_all_faculty,
    add_faculty,
    delete_faculty,
    update_faculty,
    get_all_departments
)


faculty_bp = Blueprint("faculty", __name__)


# =========================
# Faculty Page
# =========================

@faculty_bp.route("/faculty")
@faculty_bp.route("/faculty")
def faculty():

    search = request.args.get("search", "").strip()

    department = request.args.get("department", "").strip()

    faculty_list = get_all_faculty(
        search=search,
        department=department
    )

    departments = get_all_departments()

    return render_template(
        "faculty.html",
        faculty_list=faculty_list,
        departments=departments,
        search=search,
        department=department
    )


# =========================
# Add Faculty
# =========================

@faculty_bp.route("/faculty/add", methods=["POST"])
def add_faculty_route():
    name = request.form["name"]
    programme = request.form["programme"]
    department = request.form["department"]
    email = request.form["email"]

    add_faculty(
        name,
        department,
        email,
        programme
    )

    return redirect(url_for("faculty.faculty"))


# =========================
# Delete Faculty
# =========================

@faculty_bp.route("/faculty/delete/<int:id>")
def delete_faculty_route(id):

    delete_faculty(id)

    return redirect(
        url_for("faculty.faculty")
    )


# =========================
# Update Faculty
# =========================

@faculty_bp.route("/faculty/update", methods=["POST"])
def update_faculty_route():
    id = request.form["id"]
    name = request.form["name"]
    programme = request.form["programme"]
    department = request.form["department"]
    email = request.form["email"]

    update_faculty(
        id,
        name,
        department,
        email,
        programme
    )

    return redirect(url_for("faculty.faculty"))