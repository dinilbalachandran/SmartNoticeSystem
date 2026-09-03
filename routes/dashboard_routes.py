from flask import Blueprint, render_template
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

    conn.close()

    return render_template(
        "dashboard.html",
        total_notices=total_notices,
        total_faculty=total_faculty,
        total_sources=total_sources,
        total_emails_sent=total_emails_sent,
        recent_notices=recent_notices
    )