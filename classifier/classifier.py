import re


# ==========================================================
# TEXT PREPROCESSING
# ==========================================================

def normalize_text(text=""):
    """
    Convert text into a clean lowercase string.
    """

    text = text or ""

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip().lower()


def prepare_text(subject="", text=""):
    """
    Combine subject and PDF text.
    Kept for compatibility with the rest of the project.
    """

    subject = subject or ""
    text = text or ""

    combined_text = f"{subject} {text}"

    return normalize_text(combined_text)


# ==========================================================
# NOTICE TYPE CLASSIFICATION
# ==========================================================

def classify_notice_type(subject="", text=""):
    """
    Determine the general type of the notice.

    For KTU notices, the subject/title is the primary
    classification source. PDF text is used only when
    the subject does not provide enough information.
    """

    subject_content = normalize_text(subject)

    # ------------------------------------------------------
    # Recruitment / Appointment
    # Check FIRST because recruitment PDFs can contain
    # words such as "examination", "PhD", etc.
    # ------------------------------------------------------

    recruitment_keywords = [
        "recruitment",
        "appointment",
        "vacancy",
        "statutory position",
        "administrative position",
        "statutory and administrative positions",
        "positions",
        "last date for receipt of applications",
        "receipt of applications",
        "applications to various"
    ]

    for keyword in recruitment_keywords:

        if keyword in subject_content:
            return "Recruitment"

    # ------------------------------------------------------
    # Result
    # ------------------------------------------------------

    result_keywords = [
        "publication of result",
        "publication of results",
        "result publication",
        "result notification",
        "results published",
        "result",
        "results"
    ]

    for keyword in result_keywords:

        if keyword in subject_content:
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

        if keyword in subject_content:
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

        if keyword in subject_content:
            return "Admission"

    # ------------------------------------------------------
    # Academic
    # ------------------------------------------------------

    academic_keywords = [
        "academic calendar",
        "academic year",
        "course duration",
        "academic schedule"
    ]

    for keyword in academic_keywords:

        if keyword in subject_content:
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

        if keyword in subject_content:
            return "Sports"

    # ------------------------------------------------------
    # FALLBACK
    #
    # Only when the subject does not identify the type,
    # use the PDF text.
    # ------------------------------------------------------

    full_content = prepare_text(
        subject,
        text
    )

    # Remove common false-positive phrase

    full_content = full_content.replace(
        "controller of examinations",
        ""
    )

    # Recruitment fallback

    for keyword in recruitment_keywords:

        if keyword in full_content:
            return "Recruitment"

    # Result fallback

    for keyword in result_keywords:

        if keyword in full_content:
            return "Result"

    # Examination fallback

    for keyword in examination_keywords:

        if keyword in full_content:
            return "Examination"

    # Admission fallback

    for keyword in admission_keywords:

        if keyword in full_content:
            return "Admission"

    # Academic fallback

    for keyword in academic_keywords:

        if keyword in full_content:
            return "Academic"

    # Sports fallback

    for keyword in sports_keywords:

        if keyword in full_content:
            return "Sports"

    # ------------------------------------------------------
    # General
    # ------------------------------------------------------

    return "General"


# ==========================================================
# PROGRAMME CLASSIFICATION
# ==========================================================

def classify_programme(subject="", text=""):
    """
    Determine the programme from the KTU notice subject.

    The subject/title is the primary source because PDF content
    may mention other programmes that are unrelated to the notice.
    """

    subject_content = normalize_text(subject)

    # ------------------------------------------------------
    # Recruitment notices
    #
    # Do not infer a programme from the PDF for recruitment
    # notices. Recruitment PDFs may mention PhD, B.Tech, etc.
    # ------------------------------------------------------

    recruitment_keywords = [
        "recruitment",
        "appointment",
        "vacancy",
        "statutory position",
        "administrative position",
        "statutory and administrative positions",
        "positions",
        "last date for receipt of applications",
        "receipt of applications",
        "applications to various"
    ]

    for keyword in recruitment_keywords:
        if keyword in subject_content:
            return "Unknown"

    # ------------------------------------------------------
    # Programme classification from SUBJECT
    # ------------------------------------------------------

    programme_patterns = [
        ("B.HMCT", ["b.hmct", "bhmct", "b hmct"]),
        ("B.Arch", ["b.arch", "barch", "b arch"]),
        ("B.Des", ["b.des", "bdes", "b des"]),
        ("M.Tech", ["m.tech", "mtech", "m tech"]),
        ("B.Tech", ["b.tech", "btech", "b tech"]),
        ("MCA", ["mca"]),
        ("PhD", ["phd", "ph.d"]),
    ]

    for programme, keywords in programme_patterns:

        for keyword in keywords:

            if keyword in subject_content:
                return programme

    # ------------------------------------------------------
    # No programme found in subject
    #
    # Do NOT inspect PDF text here.
    # This prevents false programme classification.
    # ------------------------------------------------------

    return "Unknown"


# ==========================================================
# BRANCH CLASSIFICATION
# ==========================================================

def classify_branch(subject="", text="", programme=""):
    """
    Determine the branch from the KTU notice subject.

    The subject is the primary source. PDF text is not used for
    branch detection because it may contain unrelated branches.
    """

    subject_content = normalize_text(subject)

    # ------------------------------------------------------
    # Programmes where branch routing is not required
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
    # B.Tech branches
    # ------------------------------------------------------

    if programme == "B.Tech":

        branch_patterns = [
            ("CSE", [
                "cse",
                "computer science",
                "computer science and engineering"
            ]),
            ("ECE", [
                "ece",
                "electronics and communication",
                "electronics & communication"
            ]),
            ("EEE", [
                "eee",
                "electrical and electronics",
                "electrical & electronics"
            ]),
            ("ME", [
                "mechanical engineering",
                "me department",
                "me branch"
            ]),
            ("CE", [
                "civil engineering",
                "ce department",
                "ce branch"
            ]),
            ("IT", [
                "information technology",
                "it department",
                "it branch"
            ])
        ]

        for branch, keywords in branch_patterns:

            for keyword in keywords:

                if keyword in subject_content:
                    return branch

        # Generic B.Tech notice
        return "ALL"

    # ------------------------------------------------------
    # M.Tech branches
    # ------------------------------------------------------

    if programme == "M.Tech":

        if (
            "cse" in subject_content
            or "computer science" in subject_content
            or "computer science and engineering" in subject_content
        ):
            return "CSE"

        if (
            "ece" in subject_content
            or "electronics and communication" in subject_content
            or "electronics & communication" in subject_content
        ):
            return "ECE"

        if (
            "eee" in subject_content
            or "electrical and electronics" in subject_content
            or "electrical & electronics" in subject_content
        ):
            return "EEE"

        if "mechanical engineering" in subject_content:
            return "ME"

        if "civil engineering" in subject_content:
            return "CE"

        if "information technology" in subject_content:
            return "IT"

        return "ALL"

    # ------------------------------------------------------
    # Unknown programme
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

    subject_content = normalize_text(subject)
    full_content = prepare_text(subject, text)

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

        if keyword in subject_content:

            return "High"

    # If notice type itself is high priority

    if notice_type in [
        "Examination",
        "Result",
        "Admission"
    ]:

        return "High"

    # Fallback to PDF

    for keyword in high_priority_keywords:

        if keyword in full_content:

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

        if keyword in subject_content:

            return "Medium"

    if notice_type in [
        "Academic",
        "Sports"
    ]:

        return "Medium"

    for keyword in medium_priority_keywords:

        if keyword in full_content:

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

    tests = [

        (
            5425,
            "Extension of the last date for receipt of applications "
            "to various statutory and administrative positions "
            "up to 17.09.2026",
            """
            The application form contains references to Ph.D,
            engineering, examinations and various qualifications.
            """
        ),

        (
            5442,
            "EXAM REGISTRATION - B.Tech S8 (S,FE, Working Professional "
            "Examination, September 2026 (2019 Scheme)",
            """
            Examination registration for B.Tech students.
            """
        ),

        (
            5443,
            "KTU - Examination - Valuation(UG) - Supplementary Exam "
            "registration for B.Arch S10 (S) Exam September 2026",
            """
            Supplementary examination registration for B.Arch students.
            """
        ),

        (
            5444,
            "KTU - Examination - (UG) Valuation - Exam registration "
            "for BHMCT S3",
            """
            This PDF also contains unrelated academic terms.
            """
        ),

        (
            5445,
            "KTU - Examination - Valuation(UG) - Supplementary Exam "
            "registration for B.Des S8",
            """
            B.Des supplementary examination.
            """
        ),

        (
            5447,
            "KTU - Examination - Valuation(UG) - Supplementary Exam "
            "registration for BHMCT S8",
            """
            BHMCT supplementary examination.
            """
        ),

        (
            5448,
            "KTU - Examination - (UG) valuation - Exam registration "
            "for B.Arch S3, B.Arch S5, B.Arch S7 and B.Arch S9",
            """
            B.Arch examination registration.
            """
        )
    ]

    print()
    print("========== CLASSIFICATION TEST ==========")

    for notice_id, subject, text in tests:

        result = classify_notice(
            subject=subject,
            text=text,
            notice_id=notice_id
        )

        print()
        print(f"Notice ID: {notice_id}")
        print(f"Subject: {subject}")
        print(f"Type:      {result['notice_type']}")
        print(f"Programme: {result['programme']}")
        print(f"Branch:    {result['branch']}")
        print(f"Priority:  {result['priority']}")

    print()
    print("==========================================")