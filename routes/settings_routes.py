from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash

from database.database import get_admin_by_email


settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip()
        password = request.form["password"]

        admin = get_admin_by_email(email)

        if admin and check_password_hash(
            admin["password_hash"],
            password
        ):

            session["admin_id"] = admin["id"]
            session["admin_email"] = admin["email"]

            return redirect(url_for("dashboard.dashboard"))

        return render_template(
            "login.html",
            error="Invalid email or password"
        )

    return render_template("login.html")


@settings_bp.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("settings.login"))


@settings_bp.route("/settings")
def settings():

    if "admin_id" not in session:
        return redirect(url_for("settings.login"))

    from database.database import get_admin_by_email

    admin = get_admin_by_email(
        session["admin_email"]
    )

    return render_template(
        "settings.html",
        admin=admin
    )

@settings_bp.route("/settings/email", methods=["POST"])
def update_email():

    if "admin_id" not in session:
        return redirect(url_for("settings.login"))

    new_email = request.form["email"].strip()

    if not new_email:
        return redirect(url_for("settings.settings"))

    from database.database import update_admin_email

    update_admin_email(
        session["admin_id"],
        new_email
    )

    session["admin_email"] = new_email

    return redirect(url_for("settings.settings"))

@settings_bp.route("/settings/password", methods=["POST"])
def update_password():

    if "admin_id" not in session:
        return redirect(url_for("settings.login"))

    from database.database import (
        get_admin_by_email,
        update_admin_password
    )

    current_password = request.form["current_password"]
    new_password = request.form["new_password"]
    confirm_password = request.form["confirm_password"]

    admin = get_admin_by_email(
        session["admin_email"]
    )

    if not admin:
        return redirect(url_for("settings.settings"))

    # Check current password
    if not check_password_hash(
        admin["password_hash"],
        current_password
    ):
        return redirect(url_for("settings.settings"))

    # Check new password confirmation
    if new_password != confirm_password:
        return redirect(url_for("settings.settings"))

    # Update password
    password_hash = generate_password_hash(new_password)

    update_admin_password(
        session["admin_id"],
        password_hash
    )

    return redirect(url_for("settings.settings"))