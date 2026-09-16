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
    get_all_departments,
    get_all_academic_programmes
)


faculty_bp = Blueprint("faculty", __name__)


# =========================
# Faculty Page
# =========================

@faculty_bp.route("/faculty")
def faculty():

    search = request.args.get("search", "").strip()

    department = request.args.get("department", "").strip()

    faculty_list = get_all_faculty(
        search=search,
        department=department
    )

    departments = get_all_departments()
    academic_programmes = get_all_academic_programmes()

    return render_template(
        "faculty.html",
        faculty_list=faculty_list,
        departments=departments,
        academic_programmes=academic_programmes,
        search=search,
        department=department
    )


# =========================
# Add Faculty
# =========================

@faculty_bp.route("/faculty/add", methods=["POST"])
def faculty_add():
    name = request.form.get("name")
    department = request.form.get("department")
    email = request.form.get("email")

    # Get multiple Programme + Branch assignments
    programmes = request.form.getlist("assignment_programme")
    branches = request.form.getlist("assignment_branch")

    assignments = []

    for programme, branch in zip(programmes, branches):
        if programme and branch:
            assignments.append({
                "programme": programme,
                "branch": branch
            })

    # Use the first assignment as the old faculty.programme value
    first_programme = (
        assignments[0]["programme"]
        if assignments
        else "Unknown"
    )

    add_faculty(
        name,
        department,
        email,
        first_programme,
        assignments=assignments
    )

    return redirect(url_for("faculty.faculty_page"))


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

    faculty_id = request.form["id"]
    name = request.form["name"].strip()
    department = request.form["department"].strip()
    email = request.form["email"].strip()

    programmes = request.form.getlist("assignment_programme")
    branches = request.form.getlist("assignment_branch")

    assignments = []

    for programme, branch in zip(programmes, branches):

        if programme and branch:

            assignments.append({
                "programme": programme,
                "branch": branch
            })


    update_faculty(
        faculty_id,
        name,
        department,
        email,
        assignments=assignments
    )

    return redirect(url_for("faculty.faculty"))