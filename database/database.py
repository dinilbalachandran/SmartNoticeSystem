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

    conn.commit()
    conn.close()

# -----------------------------
# Faculty CRUD
# -----------------------------

def get_all_faculty(search="", department=""):

    conn = get_connection()

    cursor = conn.cursor()

    query = """
        SELECT *
        FROM faculty
        WHERE 1=1
    """

    parameters = []

    # Search filter
    if search:

        query += """
            AND (
                name LIKE ?
                OR programme LIKE ?
                OR department LIKE ?
                OR email LIKE ?
            )
        """

        search_value = f"%{search}%"

        parameters.extend([
            search_value,
            search_value,
            search_value,
            search_value
        ])

    # Department filter
    if department:

        query += """
            AND department = ?
        """

        parameters.append(department)

    query += """
        ORDER BY id DESC
    """

    cursor.execute(query, parameters)

    faculty = cursor.fetchall()

    conn.close()

    return faculty


def add_faculty(
    name,
    department,
    email,
    programme="Unknown"
):

    conn = get_connection()

    conn.execute("""
        INSERT INTO faculty
        (name, programme, department, email)
        VALUES (?, ?, ?, ?)
    """, (
        name,
        programme,
        department,
        email
    ))

    conn.commit()

    conn.close()

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
    programme=None
):

    conn = get_connection()

    if programme is None:

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

    else:

        conn.execute("""
            UPDATE faculty
            SET
                name = ?,
                programme = ?,
                department = ?,
                email = ?
            WHERE id = ?
        """, (
            name,
            programme,
            department,
            email,
            id
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
    priority
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
            priority
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title,
        content,
        source_id,
        notice_url,
        published_date,
        notice_type,
        programme,
        branch,
        priority
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

