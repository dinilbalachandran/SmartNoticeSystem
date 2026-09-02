from scraper.ktu_browser import scrape_ktu
from scraper.notice_parser import extract_text_from_pdf
from classifier.classifier import classify_notice
from routes.notice_router import route_notice
from database.database import (save_classified_notice, get_ktu_source_id)


def process_notices():

    data = scrape_ktu()
    source_id = get_ktu_source_id()

    if source_id is None:
        print("KTU notice source not found.")
        return

    if not data:
        print("No scraper data received.")
        return

    notices = data.get("notices", [])

    print()
    print("========== SCRAPER → CLASSIFIER ==========")
    print(f"Notices received: {len(notices)}")

    classified_count = 0

    for notice in notices:

        notice_id = notice.get("id")
        subject = notice.get("subject", "")
        attachments = notice.get("attachments", [])

        print()
        print("-------------------------------------------")
        print(f"Notice ID: {notice_id}")
        print(f"Subject: {subject}")

        for attachment in attachments:

            pdf_path = attachment.get("path")

            if not pdf_path:
                print("No PDF path found.")
                continue

            text = extract_text_from_pdf(pdf_path)

            if not text:
                print("No text extracted from PDF.")
                continue

            result = classify_notice(
                subject=subject,
                text=text,
                notice_id=notice_id
            )

            print()
            print("Classification:")
            print(f"  Type:      {result['notice_type']}")
            print(f"  Programme: {result['programme']}")
            print(f"  Branch:    {result['branch']}")
            print(f"  Priority:  {result['priority']}")

            # ------------------------------------------------------
            # Route classified notice to matching faculty
            # ------------------------------------------------------

            faculty_list = route_notice(
                result["programme"],
                result["branch"]
            )

            print()
            print("Routing:")
            print(f"  Faculty matched: {len(faculty_list)}")

            for faculty in faculty_list:
                print(
                    f"  - {faculty['name']} | "
                    f"{faculty['programme']} | "
                    f"{faculty['department']} | "
                    f"{faculty['email']}"
                )

            # ------------------------------------------------------
            # Save classified notice to database
            # ------------------------------------------------------

            notice_db_id = save_classified_notice(
                title=subject,
                content=text,
                source_id=source_id,
                notice_url="https://ktu.edu.in/Menu/announcements",
                published_date=notice.get("date"),
                notice_type=result["notice_type"],
                programme=result["programme"],
                branch=result["branch"],
                priority=result["priority"]
            )

            print()
            print(f"Database notice ID: {notice_db_id}")

            classified_count += 1

            # Only classify the first PDF for now
            break

    print()
    print("===========================================")
    print(f"Classified notices: {classified_count}")
    print("===========================================")


if __name__ == "__main__":
    process_notices()