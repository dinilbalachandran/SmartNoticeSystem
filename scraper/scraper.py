from scraper.ktu_browser import scrape_ktu
from scraper.notice_parser import extract_text_from_pdf
from classifier.classifier import classify_notice


def process_notices():

    data = scrape_ktu()

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

            classified_count += 1

            # Only classify the first PDF for now
            break

    print()
    print("===========================================")
    print(f"Classified notices: {classified_count}")
    print("===========================================")


if __name__ == "__main__":
    process_notices()