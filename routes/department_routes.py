from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

from database.database import (
    get_all_departments,
    add_department,
    update_department,
    delete_department
)


department_bp = Blueprint("department", __name__)


# =========================
# Department Page
# =========================

@department_bp.route("/departments")
def departments():

    department_list = get_all_departments()

    return render_template(
        "departments.html",
        departments=department_list
    )


# =========================
# Add Department
# =========================

@department_bp.route("/department/add", methods=["POST"])
def add_department_route():

    department_name = request.form["department_name"].strip()

    short_form = request.form["short_form"].strip().upper()

    if department_name and short_form:

        add_department(
            department_name,
            short_form
        )

    return redirect(
        url_for("department.departments")
    )


# =========================
# Update Department
# =========================

@department_bp.route("/department/update", methods=["POST"])
def update_department_route():

    id = request.form["id"]

    department_name = request.form["department_name"].strip()

    short_form = request.form["short_form"].strip().upper()

    if department_name and short_form:

        update_department(
            id,
            department_name,
            short_form
        )

    return redirect(
        url_for("department.departments")
    )


# =========================
# Delete Department
# =========================

@department_bp.route("/department/delete/<int:id>")
def delete_department_route(id):

    delete_department(id)

    return redirect(
        url_for("department.departments")
    )