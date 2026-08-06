from flask import Blueprint, render_template

notice_bp = Blueprint("notice", __name__)

@notice_bp.route("/notice-sources")
def notice_sources():
    return render_template("notice_sources.html")


@notice_bp.route("/notice-history")
def notice_history():
    return render_template("notice_history.html")