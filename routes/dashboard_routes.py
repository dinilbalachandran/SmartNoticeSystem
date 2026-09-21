from flask import Blueprint, render_template
from datetime import datetime
from database.database import get_connection

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def dashboard():

    conn = get_connection()

    total_notices = conn.execute(
        "SELECT COUNT(*) FROM notices"
    ).fetchone()[0]

    total_faculty = conn.execute(
        "SELECT COUNT(*) FROM faculty"
    ).fetchone()[0]

    total_sources = conn.execute(
        "SELECT COUNT(*) FROM notice_sources"
    ).fetchone()[0]

    total_emails_sent = conn.execute(
        "SELECT COUNT(*) FROM email_logs WHERE status = 'Sent'"
    ).fetchone()[0]

    recent_notices = conn.execute("""
        SELECT *
        FROM notices
        ORDER BY id DESC
        LIMIT 5
    """).fetchall()

    # Get the latest scheduler scan time
    last_scan = conn.execute("""
        SELECT last_checked
        FROM notice_sources
        WHERE website_name = 'KTU'
        LIMIT 1
    """).fetchone()

    conn.close()

    last_scan_time = None

    if last_scan and last_scan["last_checked"]:

        last_scan_datetime = datetime.fromisoformat(
            last_scan["last_checked"]
        )

        last_scan_time = last_scan_datetime.strftime(
            "%d %b %Y, %I:%M %p"
        )

    return render_template(
        "dashboard.html",
        total_notices=total_notices,
        total_faculty=total_faculty,
        total_sources=total_sources,
        total_emails_sent=total_emails_sent,
        recent_notices=recent_notices,
        last_scan_time=last_scan_time
    )