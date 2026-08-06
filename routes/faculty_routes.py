from flask import Blueprint, render_template

faculty_bp = Blueprint("faculty", __name__)

@faculty_bp.route("/faculty")
def faculty():
    return render_template("faculty.html")