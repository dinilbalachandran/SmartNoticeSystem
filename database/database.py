import sqlite3
from config import DATABASE


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faculty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            programme TEXT NOT NULL DEFAULT 'Unknown',
            department TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Add programme column to existing faculty table
    faculty_columns = cursor.execute(
        "PRAGMA table_info(faculty)"
    ).fetchall()

    column_names = [
        column["name"]
        for column in faculty_columns
    ]

    if "programme" not in column_names:
        cursor.execute("""
            ALTER TABLE faculty
            ADD COLUMN programme TEXT NOT NULL DEFAULT 'Unknown'
        """)

    # -------------------------------------
    # Admin Account
    # -------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_account (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            department_name TEXT UNIQUE NOT NULL,

            short_form TEXT UNIQUE NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notice_sources (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            website_name TEXT NOT NULL,

            website_url TEXT NOT NULL,

            check_interval INTEGER NOT NULL,

            status TEXT NOT NULL DEFAULT 'Active',

            last_checked TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notices (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            content TEXT,

            source_id INTEGER,

            notice_url TEXT,

            published_date TEXT,

            detected_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            category TEXT,

            status TEXT NOT NULL DEFAULT 'New',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (source_id)
                REFERENCES notice_sources(id)

        )
    """)

    # -----------------------------
    # Email Logs
    # -----------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_logs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            notice_id INTEGER NOT NULL,

            faculty_id INTEGER NOT NULL,

            recipient_email TEXT NOT NULL,

            subject TEXT NOT NULL,

            status TEXT NOT NULL DEFAULT 'Pending',

            sent_at TIMESTAMP,

            error_message TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (notice_id)
                REFERENCES notices(id)
                ON DELETE CASCADE,

            FOREIGN KEY (faculty_id)
                REFERENCES faculty(id)
                ON DELETE CASCADE

        )
    """)

    # ------------------------------------------------------
    # Migration: Add classification fields to notices
    # ------------------------------------------------------

    notice_columns = cursor.execute(
        "PRAGMA table_info(notices)"
    ).fetchall()

    notice_column_names = [
        column["name"]
        for column in notice_columns
    ]

    if "programme" not in notice_column_names:
        cursor.execute("""
            ALTER TABLE notices
            ADD COLUMN programme TEXT NOT NULL DEFAULT 'Unknown'
        """)

    if "branch" not in notice_column_names:
        cursor.execute("""
            ALTER TABLE notices
            ADD COLUMN branch TEXT NOT NULL DEFAULT 'ALL'
        """)

    if "priority" not in notice_column_names:
        cursor.execute("""
            ALTER TABLE notices
            ADD COLUMN priority TEXT NOT NULL DEFAULT 'Low'
        """)

    if "pdf_path" not in notice_column_names:
        cursor.execute("""
            ALTER TABLE notices
            ADD COLUMN pdf_path TEXT
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notice_departments (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            notice_id INTEGER NOT NULL,

            department_id INTEGER NOT NULL,

            FOREIGN KEY (notice_id)
                REFERENCES notices(id)
                ON DELETE CASCADE,

            FOREIGN KEY (department_id)
                REFERENCES departments(id)
                ON DELETE CASCADE,

            UNIQUE(notice_id, department_id)

        )
    """)

    # -------------------------------------
    # Faculty Teaching Assignments
    # -------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faculty_teaching_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            faculty_id INTEGER NOT NULL,
            programme TEXT NOT NULL,
            branch TEXT NOT NULL,
            FOREIGN KEY (faculty_id)
                REFERENCES faculty(id)
                ON DELETE CASCADE,
            UNIQUE(faculty_id, programme, branch)
        )
    """)

    # -------------------------------------
    # Academic Programme + Branch
    # -------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS academic_programmes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            programme TEXT NOT NULL,
            branch TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(programme, branch)
        )
    """)

    # # Migrate existing faculty records
    # cursor.execute("""
    #     INSERT OR IGNORE INTO faculty_teaching_assignments
    #     (faculty_id, programme, branch)
    #     SELECT
    #         id,
    #         programme,
    #         department
    #     FROM faculty
    #     WHERE programme IS NOT NULL
    #       AND programme != ''
    #       AND department IS NOT NULL
    #       AND department != ''
    # """)

    conn.commit()
    conn.close()

# -----------------------------
# Faculty CRUD
# -----------------------------

def get_all_faculty(search="", department=""):
    conn = get_connection()

    query = """
        SELECT
            f.id,
            f.name,
            f.email,
            f.department,
            GROUP_CONCAT(
                fta.programme || ' ' || fta.branch,
                ', '
            ) AS assignments
        FROM faculty f
        LEFT JOIN faculty_teaching_assignments fta
            ON f.id = fta.faculty_id
        WHERE 1=1
    """

    params = []

    if search:
        query += """
            AND (
                f.name LIKE ?
                OR f.email LIKE ?
                OR f.department LIKE ?
                OR fta.programme LIKE ?
                OR fta.branch LIKE ?
            )
        """
        search_value = f"%{search}%"
        params.extend([
            search_value,
            search_value,
            search_value,
            search_value,
            search_value
        ])

    if department:
        query += " AND f.department = ?"
        params.append(department)

    query += """
        GROUP BY f.id
        ORDER BY f.name
    """

    faculty = conn.execute(query, params).fetchall()
    conn.close()

    return [dict(row) for row in faculty]


def add_faculty(name, department, email, programme="Unknown", branch=None, assignments=None):
    conn = get_connection()

    cursor = conn.execute("""
        INSERT INTO faculty (name, programme, department, email)
        VALUES (?, ?, ?, ?)
    """, (name, programme, department, email))

    faculty_id = cursor.lastrowid

    # New multiple Programme + Branch assignments
    if assignments:
        for assignment in assignments:
            assignment_programme = assignment.get("programme")
            assignment_branch = assignment.get("branch")

            if assignment_programme and assignment_branch:
                conn.execute("""
                    INSERT OR IGNORE INTO faculty_teaching_assignments
                    (faculty_id, programme, branch)
                    VALUES (?, ?, ?)
                """, (
                    faculty_id,
                    assignment_programme,
                    assignment_branch
                ))

    # Backward compatibility for old single assignment
    elif programme and branch:
        conn.execute("""
            INSERT OR IGNORE INTO faculty_teaching_assignments
            (faculty_id, programme, branch)
            VALUES (?, ?, ?)
        """, (faculty_id, programme, branch))

    conn.commit()
    conn.close()

    return faculty_id

def delete_faculty(faculty_id):

    conn = get_connection()

    conn.execute(
        "DELETE FROM faculty WHERE id=?",
        (faculty_id,)
    )

    conn.commit()

    conn.close()

def update_faculty(
    id,
    name,
    department,
    email,
    assignments=None
):
    conn = get_connection()

    # Update basic faculty information
    conn.execute("""
        UPDATE faculty
        SET
            name = ?,
            department = ?,
            email = ?
        WHERE id = ?
    """, (
        name,
        department,
        email,
        id
    ))


    # Update teaching assignments
    if assignments is not None:

        # Remove old assignments
        conn.execute("""
            DELETE FROM faculty_teaching_assignments
            WHERE faculty_id = ?
        """, (id,))


        # Add new assignments
        for assignment in assignments:

            programme = assignment.get("programme")
            branch = assignment.get("branch")

            if programme and branch:

                conn.execute("""
                    INSERT OR IGNORE INTO faculty_teaching_assignments
                    (faculty_id, programme, branch)
                    VALUES (?, ?, ?)
                """, (
                    id,
                    programme,
                    branch
                ))


    conn.commit()
    conn.close()

# -------------------------------------
# Department CRUD
# -------------------------------------

def get_all_departments():

    conn = get_connection()

    departments = conn.execute("""
        SELECT *
        FROM departments
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return departments


def add_department(department_name, short_form):

    conn = get_connection()

    conn.execute("""
        INSERT INTO departments
        (department_name, short_form)
        VALUES (?, ?)
    """, (
        department_name,
        short_form
    ))

    conn.commit()

    conn.close()


def update_department(id, department_name, short_form):

    conn = get_connection()

    conn.execute("""
        UPDATE departments

        SET
            department_name = ?,
            short_form = ?

        WHERE id = ?
    """, (
        department_name,
        short_form,
        id
    ))

    conn.commit()

    conn.close()


def delete_department(id):

    conn = get_connection()

    conn.execute(
        "DELETE FROM departments WHERE id=?",
        (id,)
    )

    conn.commit()

    conn.close()

# -------------------------------------
# Academic Programme + Branch CRUD
# -------------------------------------

def get_all_academic_programmes():
    conn = get_connection()

    programmes = conn.execute("""
        SELECT *
        FROM academic_programmes
        ORDER BY programme, branch
    """).fetchall()

    conn.close()

    return programmes


def add_academic_programme(programme, branch):
    conn = get_connection()

    conn.execute("""
        INSERT INTO academic_programmes
        (programme, branch)
        VALUES (?, ?)
    """, (
        programme,
        branch
    ))

    conn.commit()
    conn.close()


def update_academic_programme(id, programme, branch):
    conn = get_connection()

    conn.execute("""
        UPDATE academic_programmes
        SET
            programme = ?,
            branch = ?
        WHERE id = ?
    """, (
        programme,
        branch,
        id
    ))

    conn.commit()
    conn.close()


def delete_academic_programme(id):
    conn = get_connection()

    conn.execute(
        "DELETE FROM academic_programmes WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

# -------------------------------------
# Notice Sources CRUD
# -------------------------------------

def get_all_notice_sources():

    conn = get_connection()

    sources = conn.execute("""
        SELECT *
        FROM notice_sources
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return sources


def get_ktu_source_id():

    conn = get_connection()

    source = conn.execute("""
        SELECT id
        FROM notice_sources
        WHERE website_url = ?
        LIMIT 1
    """, (
        "https://ktu.edu.in/Menu/announcements",
    )).fetchone()

    conn.close()

    if source:
        return source["id"]

    return None

def add_notice_source(name, url, interval):

    conn = get_connection()

    conn.execute("""
        INSERT INTO notice_sources
        (website_name, website_url, check_interval)
        VALUES (?, ?, ?)
    """, (name, url, interval))

    conn.commit()

    conn.close()


def update_notice_source(id, name, url, interval, status):

    conn = get_connection()

    conn.execute("""
        UPDATE notice_sources

        SET

            website_name=?,
            website_url=?,
            check_interval=?,
            status=?

        WHERE id=?
    """, (name, url, interval, status, id))

    conn.commit()

    conn.close()


def delete_notice_source(id):

    conn = get_connection()

    conn.execute(
        "DELETE FROM notice_sources WHERE id=?",
        (id,)
    )

    conn.commit()

    conn.close()


# =====================================
# Notice CRUD
# =====================================

def add_notice(
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
):

    conn = get_connection()

    cursor = conn.cursor()

    # Add notice
    cursor.execute("""
        INSERT INTO notices
        (
            title,
            content,
            source_id,
            notice_url,
            published_date,
            category,
            programme,
            branch,
            priority
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title,
        content,
        source_id,
        notice_url,
        published_date,
        category,
        programme,
        branch,
        priority
    ))

    notice_id = cursor.lastrowid

    # Assign departments
    for department_id in department_ids:

        cursor.execute("""
            INSERT INTO notice_departments
            (
                notice_id,
                department_id
            )
            VALUES (?, ?)
        """, (
            notice_id,
            department_id
        ))

    conn.commit()

    conn.close()

    return notice_id

def save_classified_notice(
    title,
    content,
    source_id,
    notice_url,
    published_date,
    notice_type,
    programme,
    branch,
    priority,
    pdf_path=None
):

    conn = get_connection()

    # ------------------------------------------------------
    # Prevent duplicate notices
    # ------------------------------------------------------

    existing = conn.execute("""
        SELECT id
        FROM notices
        WHERE title = ?
          AND source_id = ?
    """, (
        title,
        source_id
    )).fetchone()

    if existing:
        conn.execute(
            """
            UPDATE notices
            SET
                content = ?,
                category = ?,
                programme = ?,
                branch = ?,
                priority = ?,
                pdf_path = COALESCE(?, pdf_path)
            WHERE id = ?
            """,
            (
                content,
                notice_type,
                programme,
                branch,
                priority,
                pdf_path,
                existing["id"]
            )
        )

        conn.commit()
        conn.close()
        return existing["id"]

    # ------------------------------------------------------
    # Save classified notice
    # ------------------------------------------------------

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO notices
        (
            title,
            content,
            source_id,
            notice_url,
            published_date,
            category,
            programme,
            branch,
            priority,
            pdf_path
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title,
        content,
        source_id,
        notice_url,
        published_date,
        notice_type,
        programme,
        branch,
        priority,
        pdf_path
    ))

    notice_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return notice_id

def get_all_notices(search=""):

    conn = get_connection()

    cursor = conn.cursor()

    if search:

        cursor.execute("""
            SELECT
                notices.*,
                notice_sources.website_name

            FROM notices

            LEFT JOIN notice_sources
                ON notices.source_id = notice_sources.id

            WHERE
                notices.title LIKE ?
                OR notices.content LIKE ?
                OR notices.category LIKE ?

            ORDER BY notices.id DESC
        """, (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ))

    else:

        cursor.execute("""
            SELECT
                notices.*,
                notice_sources.website_name

            FROM notices

            LEFT JOIN notice_sources
                ON notices.source_id = notice_sources.id

            ORDER BY notices.id DESC
        """)

    notices = cursor.fetchall()

    conn.close()

    return notices


def get_notice_by_id(notice_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            notices.*,
            notice_sources.website_name

        FROM notices

        LEFT JOIN notice_sources
            ON notices.source_id = notice_sources.id

        WHERE notices.id = ?
    """, (notice_id,))

    notice = cursor.fetchone()

    conn.close()

    return notice


def get_notice_departments(notice_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            departments.id,
            departments.department_name,
            departments.short_form

        FROM departments

        INNER JOIN notice_departments

            ON departments.id =
               notice_departments.department_id

        WHERE notice_departments.notice_id = ?

        ORDER BY departments.department_name
    """, (notice_id,))

    departments = cursor.fetchall()

    conn.close()

    return departments


def delete_notice(notice_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM notice_departments
        WHERE notice_id = ?
    """, (notice_id,))

    cursor.execute("""
        DELETE FROM notices
        WHERE id = ?
    """, (notice_id,))

    conn.commit()

    conn.close()



def create_email_log(
    notice_id,
    faculty_id,
    recipient_email,
    subject
):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO email_logs
        (
            notice_id,
            faculty_id,
            recipient_email,
            subject,
            status
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        notice_id,
        faculty_id,
        recipient_email,
        subject,
        "Pending"
    ))

    log_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return log_id


def update_email_log(
    log_id,
    status,
    error_message=None
):
    conn = get_connection()

    if status == "Sent":

        conn.execute("""
            UPDATE email_logs
            SET
                status = ?,
                sent_at = CURRENT_TIMESTAMP,
                error_message = ?
            WHERE id = ?
        """, (
            status,
            error_message,
            log_id
        ))

    else:

        conn.execute("""
            UPDATE email_logs
            SET
                status = ?,
                error_message = ?
            WHERE id = ?
        """, (
            status,
            error_message,
            log_id
        ))

    conn.commit()
    conn.close()

def email_already_sent(notice_id, faculty_id):
    conn = get_connection()

    existing = conn.execute("""
        SELECT id
        FROM email_logs
        WHERE notice_id = ?
          AND faculty_id = ?
          AND status = 'Sent'
        LIMIT 1
    """, (
        notice_id,
        faculty_id
    )).fetchone()

    conn.close()

    return existing is not None

def update_source_last_checked(source_id):
    conn = get_connection()

    conn.execute("""
        UPDATE notice_sources
        SET last_checked = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (source_id,))

    conn.commit()
    conn.close()

# -------------------------------------
# Admin Account Functions
# -------------------------------------

def create_admin(email, password_hash):

    conn = get_connection()

    conn.execute("""
        INSERT INTO admin_account (email, password_hash)
        VALUES (?, ?)
    """, (
        email,
        password_hash
    ))

    conn.commit()
    conn.close()


def get_admin_by_email(email):

    conn = get_connection()

    admin = conn.execute("""
        SELECT *
        FROM admin_account
        WHERE email = ?
    """, (
        email,
    )).fetchone()

    conn.close()

    return dict(admin) if admin else None


def update_admin_email(admin_id, email):

    conn = get_connection()

    conn.execute("""
        UPDATE admin_account
        SET email = ?
        WHERE id = ?
    """, (
        email,
        admin_id
    ))

    conn.commit()
    conn.close()


def update_admin_password(admin_id, password_hash):

    conn = get_connection()

    conn.execute("""
        UPDATE admin_account
        SET password_hash = ?
        WHERE id = ?
    """, (
        password_hash,
        admin_id
    ))

    conn.commit()
    conn.close()