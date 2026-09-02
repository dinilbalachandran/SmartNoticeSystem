from database.database import get_connection


def route_notice(programme, branch):
    """
    Find faculty members who should receive a classified notice.

    Routing rules:
    - Specific programme + specific branch
      Example: B.Tech + CSE
    - Specific programme + ALL branches
      Example: B.Tech + ALL
    - Programme-specific courses such as MCA
      use the programme with ALL branch.
    """

    conn = get_connection()

    # Do not route notices when programme is unknown
    if not programme or programme == "Unknown":
        conn.close()
        return []

    # ------------------------------------------------------
    # Specific branch
    # Example: B.Tech + CSE
    # ------------------------------------------------------
    if branch != "ALL":
        faculty = conn.execute("""
            SELECT *
            FROM faculty
            WHERE programme = ?
              AND department = ?
            ORDER BY name
        """, (programme, branch)).fetchall()

    # ------------------------------------------------------
    # All branches of a programme
    # Example: B.Tech + ALL
    # ------------------------------------------------------
    else:
        faculty = conn.execute("""
            SELECT *
            FROM faculty
            WHERE programme = ?
            ORDER BY name
        """, (programme,)).fetchall()

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