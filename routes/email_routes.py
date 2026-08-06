from flask import Blueprint, render_template

email_bp = Blueprint("email", __name__)

@email_bp.route("/email-logs")
def email_logs():
    return render_template("email_logs.html")