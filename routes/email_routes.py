from flask import Blueprint, render_template

from database.database import get_connection


email_bp = Blueprint("email", __name__)


@email_bp.route("/email-logs")
def email_logs():

    conn = get_connection()

    logs = conn.execute("""
        SELECT
            email_logs.*,
            notices.title AS notice_title,
            faculty.name AS faculty_name
        FROM email_logs
        JOIN notices
            ON email_logs.notice_id = notices.id
        JOIN faculty
            ON email_logs.faculty_id = faculty.id
        ORDER BY email_logs.created_at DESC
    """).fetchall()

    conn.close()

    return render_template(
        "email_logs.html",
        logs=logs
    )