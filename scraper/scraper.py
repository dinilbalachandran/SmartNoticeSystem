from scraper.ktu_browser import scrape_ktu
from scraper.notice_parser import extract_text_from_pdf


def process_notices():

    print("Getting notices through KTU browser...")

    data = scrape_ktu()

    if not data:
        print("Could not retrieve notices from KTU.")
        return

    notices = data.get("notices", [])

    print()
    print("========== SCRAPER RESULT ==========")

    print(
        "Total notices:",
        data.get("totalElements", "Unknown")
    )

    print(
        "Notices received:",
        len(notices)
    )

    # --------------------------------------------------
    # Process notices
    # --------------------------------------------------

    for notice in notices:

        notice_id = notice.get("id")
        subject = notice.get("subject")
        announcement_date = notice.get("date")

        print()
        print("========================================")

        print("ID:", notice_id)
        print("Date:", announcement_date)
        print("Subject:", subject)

        attachments = notice.get(
            "attachments",
            []
        )

        print(
            "Attachments:",
            len(attachments)
        )

        # --------------------------------------------------
        # Process downloaded PDFs
        # --------------------------------------------------

        for attachment in attachments:

            pdf_path = attachment.get("path")

            if not pdf_path:

                print(
                    "PDF was not downloaded."
                )

                continue

            print(
                "PDF:",
                pdf_path
            )

            # --------------------------------------------------
            # Extract PDF text
            # --------------------------------------------------

            try:

                text = extract_text_from_pdf(
                    pdf_path
                )

                if text:

                    print(
                        "Extracted text:",
                        f"{len(text):,}",
                        "characters"
                    )

                else:

                    print(
                        "No text could be extracted."
                    )

            except Exception as e:

                print(
                    "PDF parsing error:",
                    e
                )

    print()
    print(
        "========== SCRAPER FINISHED =========="
    )


if __name__ == "__main__":

    process_notices()