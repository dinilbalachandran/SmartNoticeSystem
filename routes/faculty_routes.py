from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

from database.database import (
    get_all_faculty,
    add_faculty,
    delete_faculty,
    update_faculty
)

faculty_bp = Blueprint("faculty", __name__)


@faculty_bp.route("/faculty")
def faculty():

    faculty_list = get_all_faculty()

    return render_template(
        "faculty.html",
        faculty_list=faculty_list
    )


@faculty_bp.route("/faculty/add", methods=["POST"])
def add_faculty_route():

    name = request.form["name"]

    department = request.form["department"]

    email = request.form["email"]

    add_faculty(name, department, email)

    return redirect(url_for("faculty.faculty"))

@faculty_bp.route("/faculty/delete/<int:id>")
def delete_faculty_route(id):

    delete_faculty(id)

    return redirect(url_for("faculty.faculty"))

@faculty_bp.route("/faculty/update", methods=["POST"])
def update_faculty_route():

    id = request.form["id"]
    name = request.form["name"]
    department = request.form["department"]
    email = request.form["email"]

    update_faculty(id, name, department, email)

    return redirect(url_for("faculty.faculty"))