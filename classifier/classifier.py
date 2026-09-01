import re


# ==========================================================
# TEXT PREPROCESSING
# ==========================================================

def prepare_text(subject="", text=""):
    """
    Combine the notice subject and extracted PDF text
    into one searchable lowercase string.
    """

    subject = subject or ""
    text = text or ""

    combined_text = f"{subject} {text}"

    # Convert multiple spaces/newlines into one space
    combined_text = re.sub(
        r"\s+",
        " ",
        combined_text
    )

    return combined_text.strip().lower()


# ==========================================================
# NOTICE TYPE CLASSIFICATION
# ==========================================================

def classify_notice_type(subject="", text=""):
    """
    Determine the general type of the notice.
    """

    content = prepare_text(
        subject,
        text
    )

    # ------------------------------------------------------
    # Result
    # ------------------------------------------------------

    result_keywords = [
        "publication of result",
        "publication of results",
        "result publication",
        "results",
        "result"
    ]

    for keyword in result_keywords:
        if keyword in content:
            return "Result"


    # ------------------------------------------------------
    # Examination
    # ------------------------------------------------------

    examination_keywords = [
        "examination",
        "exam",
        "time table",
        "timetable",
        "hall ticket",
        "exam registration",
        "examination registration"
    ]

    for keyword in examination_keywords:
        if keyword in content:
            return "Examination"

    # ------------------------------------------------------
    # Admission
    # ------------------------------------------------------

    admission_keywords = [
        "admission",
        "spot admission",
        "allotment",
        "application for admission"
    ]

    for keyword in admission_keywords:
        if keyword in content:
            return "Admission"

    # ------------------------------------------------------
    # Academic
    # ------------------------------------------------------

    academic_keywords = [
        "academic calendar",
        "academic",
        "semester",
        "course duration"
    ]

    for keyword in academic_keywords:
        if keyword in content:
            return "Academic"

    # ------------------------------------------------------
    # Sports
    # ------------------------------------------------------

    sports_keywords = [
        "sports",
        "sport",
        "athletic",
        "tournament",
        "championship"
    ]

    for keyword in sports_keywords:
        if keyword in content:
            return "Sports"

    # ------------------------------------------------------
    # Recruitment / Appointment
    # ------------------------------------------------------

    recruitment_keywords = [
        "recruitment",
        "appointment",
        "vacancy",
        "statutory position",
        "administrative position"
    ]

    for keyword in recruitment_keywords:
        if keyword in content:
            return "Recruitment"

    # ------------------------------------------------------
    # General
    # ------------------------------------------------------

    return "General"


# ==========================================================
# PROGRAMME CLASSIFICATION
# ==========================================================

def classify_programme(subject="", text=""):
    """
    Identify the academic programme mentioned in the notice.
    """

    content = prepare_text(
        subject,
        text
    )

    # ------------------------------------------------------
    # M.Tech
    # ------------------------------------------------------

    if re.search(
        r"\bm\s*\.?\s*tech\b|\bmtech\b",
        content,
        re.IGNORECASE
    ):
        return "M.Tech"

    # ------------------------------------------------------
    # B.Tech
    # ------------------------------------------------------

    if re.search(
        r"\bb\s*\.?\s*tech\b|\bbtech\b",
        content,
        re.IGNORECASE
    ):
        return "B.Tech"

    # ------------------------------------------------------
    # MCA
    # ------------------------------------------------------

    if re.search(
        r"\bmca\b",
        content,
        re.IGNORECASE
    ):
        return "MCA"

    # ------------------------------------------------------
    # B.Des
    # ------------------------------------------------------

    if re.search(
        r"\bb\s*\.?\s*des\b|\bbdes\b",
        content,
        re.IGNORECASE
    ):
        return "B.Des"

    # ------------------------------------------------------
    # B.Arch
    # ------------------------------------------------------

    if re.search(
        r"\bb\s*\.?\s*arch\b|\bbarch\b",
        content,
        re.IGNORECASE
    ):
        return "B.Arch"

    # ------------------------------------------------------
    # B.HMCT
    # ------------------------------------------------------

    if re.search(
        r"\bb\s*\.?\s*hmct\b|\bhmct\b",
        content,
        re.IGNORECASE
    ):
        return "B.HMCT"

    # ------------------------------------------------------
    # PhD
    # ------------------------------------------------------

    if re.search(
        r"\bph\s*\.?\s*d\b|\bphd\b",
        content,
        re.IGNORECASE
    ):
        return "PhD"

    return "Unknown"


# ==========================================================
# BRANCH CLASSIFICATION
# ==========================================================

def classify_branch(
    subject="",
    text="",
    programme=None
):
    """
    Identify the specific branch/department.

    This function currently uses keyword matching.
    It will be expanded after examining actual KTU
    notice contents.
    """

    content = prepare_text(
        subject,
        text
    )

    # ------------------------------------------------------
    # Programme-specific handling
    # ------------------------------------------------------

    if programme in [
        "B.Arch",
        "B.HMCT",
        "B.Des",
        "MCA",
        "PhD"
    ]:
        return "ALL"

    # ------------------------------------------------------
    # Computer Science
    # ------------------------------------------------------

    if (
        "computer science and engineering" in content
        or "computer science" in content
        or re.search(r"\bcse\b", content)
    ):
        return "CSE"

    # ------------------------------------------------------
    # Electronics and Communication
    # ------------------------------------------------------

    if (
        "electronics and communication engineering"
        in content
        or "electronics & communication engineering"
        in content
        or re.search(r"\bece\b", content)
    ):
        return "ECE"

    # ------------------------------------------------------
    # Electrical and Electronics
    # ------------------------------------------------------

    if (
        "electrical and electronics engineering"
        in content
        or "electrical & electronics engineering"
        in content
        or re.search(r"\beee\b", content)
    ):
        return "EEE"

    # ------------------------------------------------------
    # Mechanical
    # ------------------------------------------------------

    if (
        "mechanical engineering" in content
        or re.search(r"\bme\b", content)
    ):
        return "ME"

    # ------------------------------------------------------
    # Civil
    # ------------------------------------------------------

    if (
        "civil engineering" in content
        or re.search(r"\bce\b", content)
    ):
        return "CE"

    # ------------------------------------------------------
    # Information Technology
    # ------------------------------------------------------

    if (
        "information technology" in content
        or re.search(r"\bit\b", content)
    ):
        return "IT"

    # ------------------------------------------------------
    # Architecture
    # ------------------------------------------------------

    if (
        "architecture" in content
        or re.search(r"\barch\b", content)
    ):
        return "Architecture"

    # ------------------------------------------------------
    # No specific branch found
    # ------------------------------------------------------

    return "ALL"


# ==========================================================
# PRIORITY CLASSIFICATION
# ==========================================================

def classify_priority(
    subject="",
    text="",
    notice_type=None
):
    """
    Assign notice priority.

    High:
        Examination, results, deadlines, admissions

    Medium:
        Academic and sports related notices

    Low:
        General notices
    """

    content = prepare_text(
        subject,
        text
    )

    # ------------------------------------------------------
    # High priority
    # ------------------------------------------------------

    high_priority_keywords = [
        "examination",
        "exam",
        "result",
        "results",
        "admission",
        "last date",
        "deadline",
        "urgent",
        "registration"
    ]

    for keyword in high_priority_keywords:
        if keyword in content:
            return "High"

    if notice_type in [
        "Examination",
        "Result",
        "Admission"
    ]:
        return "High"

    # ------------------------------------------------------
    # Medium priority
    # ------------------------------------------------------

    medium_priority_keywords = [
        "academic",
        "academic calendar",
        "sports",
        "tournament",
        "event"
    ]

    for keyword in medium_priority_keywords:
        if keyword in content:
            return "Medium"

    if notice_type in [
        "Academic",
        "Sports"
    ]:
        return "Medium"

    # ------------------------------------------------------
    # Low priority
    # ------------------------------------------------------

    return "Low"


# ==========================================================
# COMPLETE CLASSIFICATION
# ==========================================================

def classify_notice(
    subject="",
    text="",
    notice_id=None
):
    """
    Perform complete notice classification.
    """

    notice_type = classify_notice_type(
        subject,
        text
    )

    programme = classify_programme(
        subject,
        text
    )

    branch = classify_branch(
        subject,
        text,
        programme
    )

    priority = classify_priority(
        subject,
        text,
        notice_type
    )

    return {
        "notice_id": notice_id,
        "notice_type": notice_type,
        "programme": programme,
        "branch": branch,
        "priority": priority
    }


# ==========================================================
# TEMPORARY TEST
# ==========================================================

if __name__ == "__main__":

    subject = (
    "B.Tech Computer Science and Engineering - "
    "Semester Examination Result Notification"
    )

    text = """
    The B.Tech Computer Science and Engineering S3 examination
    results have been published. Students can check their results
    through the university portal.
    """

    result = classify_notice(
        subject=subject,
        text=text,
        notice_id=5432
    )

    print()
    print("========== CLASSIFICATION RESULT ==========")

    for key, value in result.items():
        print(
            f"{key}: {value}"
        )

    print(
        "==========================================="
    )