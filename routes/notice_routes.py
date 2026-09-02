from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

from database.database import (
    get_all_notice_sources,
    add_notice_source,
    update_notice_source,
    delete_notice_source,
    get_all_notices,
    get_notice_by_id,
    get_notice_departments,
    get_all_departments,
    add_notice
)

notice_bp = Blueprint("notice", __name__)


@notice_bp.route("/notice-sources")
def notice_sources():

    sources = get_all_notice_sources()

    return render_template(
        "notice_sources.html",
        sources=sources
    )

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

# =========================
# Notice History
# =========================

@notice_bp.route("/notice-history")
def notice_history():

    search = request.args.get("search", "").strip()

    notices = get_all_notices(search=search)

    sources = get_all_notice_sources()

    departments = get_all_departments()

    return render_template(
        "notice_history.html",
        notices=notices,
        search=search,
        sources=sources,
        departments=departments
    )

# =========================
# Notice Details
# =========================

@notice_bp.route("/notice/<int:id>")
def notice_details(id):

    notice = get_notice_by_id(id)

    if notice is None:
        return "Notice not found", 404

    departments = get_notice_departments(id)

    return render_template(
        "notice_details.html",
        notice=notice,
        departments=departments
    )

# =========================
# Add Notice
# =========================

@notice_bp.route("/notice/add", methods=["POST"])
def add_notice_route():

    title = request.form["title"]

    content = request.form["content"]

    source_id = request.form["source_id"]

    notice_url = request.form["notice_url"]

    published_date = request.form["published_date"]

    category = request.form["category"]

    department_ids = request.form.getlist("department_ids")

    add_notice(
        title,
        content,
        source_id,
        notice_url,
        published_date,
        category,
        department_ids,
        programme="Unknown",
        branch="ALL",
        priority="Low"
    )

    return redirect(
        url_for("notice.notice_history")
    )