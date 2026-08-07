from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

from database.database import (
    get_all_notice_sources,
    add_notice_source,
    update_notice_source,
    delete_notice_source
)

notice_bp = Blueprint("notice", __name__)


@notice_bp.route("/notice-sources")
def notice_sources():

    sources = get_all_notice_sources()

    return render_template(
        "notice_sources.html",
        sources=sources
    )

@notice_bp.route("/notice-history")
def notice_history():

    return render_template("notice_history.html")

@notice_bp.route("/notice-source/add", methods=["POST"])
def add_notice_source_route():

    name = request.form["website_name"]

    url = request.form["website_url"]

    interval = request.form["check_interval"]

    add_notice_source(name, url, interval)

    return redirect(url_for("notice.notice_sources"))

@notice_bp.route("/notice-source/update", methods=["POST"])
def update_notice_source_route():

    id = request.form["id"]

    name = request.form["website_name"]

    url = request.form["website_url"]

    interval = request.form["check_interval"]

    status = request.form["status"]

    update_notice_source(
        id,
        name,
        url,
        interval,
        status
    )

    return redirect(
        url_for("notice.notice_sources")
    )

@notice_bp.route("/notice-source/delete/<int:id>")
def delete_notice_source_route(id):

    delete_notice_source(id)

    return redirect(url_for("notice.notice_sources"))