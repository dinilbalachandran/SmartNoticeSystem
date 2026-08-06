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

            department TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    conn.commit()
    conn.close()

# -----------------------------
# Faculty CRUD
# -----------------------------

def get_all_faculty():

    conn = get_connection()

    faculty = conn.execute("""
        SELECT *
        FROM faculty
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return faculty


def add_faculty(name, department, email):

    conn = get_connection()

    conn.execute("""
        INSERT INTO faculty
        (name, department, email)
        VALUES (?, ?, ?)
    """, (name, department, email))

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

def update_faculty(id, name, department, email):

    conn = get_connection()

    conn.execute("""
        UPDATE faculty
        SET
            name = ?,
            department = ?,
            email = ?
        WHERE id = ?
    """, (name, department, email, id))

    conn.commit()

    conn.close()