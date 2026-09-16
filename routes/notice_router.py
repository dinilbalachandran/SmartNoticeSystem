from database.database import get_connection


def route_notice(programme, branch):

    conn = get_connection()

    # ------------------------------------------------------
    # Unknown programme → send to all faculty
    # ------------------------------------------------------
    if not programme or programme == "Unknown":

        faculty = conn.execute("""
            SELECT DISTINCT f.*
            FROM faculty f
            ORDER BY f.name
        """).fetchall()

        conn.close()

        return [dict(row) for row in faculty]

    # ------------------------------------------------------
    # Specific branch → exact Programme + Branch match
    # ------------------------------------------------------
    if branch != "ALL":

        faculty = conn.execute("""
            SELECT DISTINCT f.*
            FROM faculty f
            INNER JOIN faculty_teaching_assignments fta
                ON f.id = fta.faculty_id
            WHERE fta.programme = ?
              AND fta.branch = ?
            ORDER BY f.name
        """, (
            programme,
            branch
        )).fetchall()

    # ------------------------------------------------------
    # ALL branches → all faculty teaching that programme
    # ------------------------------------------------------
    else:

        faculty = conn.execute("""
            SELECT DISTINCT f.*
            FROM faculty f
            INNER JOIN faculty_teaching_assignments fta
                ON f.id = fta.faculty_id
            WHERE fta.programme = ?
            ORDER BY f.name
        """, (
            programme,
        )).fetchall()

    conn.close()

    return [dict(row) for row in faculty]


if __name__ == "__main__":

    print()
    print("========== NOTICE ROUTING TEST ==========")

    programme = "M.Tech"
    branch = "ALL"

    faculty_list = route_notice(
        programme,
        branch
    )

    print(f"Programme: {programme}")
    print(f"Branch:    {branch}")
    print()

    print("Faculty to receive notice:")

    for faculty in faculty_list:
        print(
            f"- {faculty['name']} | "
            f"{faculty['programme']} | "
            f"{faculty['department']} | "
            f"{faculty['email']}"
        )

    print()
    print(f"Total faculty: {len(faculty_list)}")
    print("==========================================")