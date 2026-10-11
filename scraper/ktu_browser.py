import base64
import json
import re
import os
import subprocess
import time
import requests
from pathlib import Path

from playwright.sync_api import sync_playwright


KTU_ANNOUNCEMENTS_PAGE = (
    "https://ktu.edu.in/Menu/announcements"
)

ANNOUNCEMENTS_URL = (
    "https://api.ktu.edu.in/"
    "ktu-web-portal-api/anon/announcemnts"
)

ATTACHMENT_URL = (
    "https://api.ktu.edu.in/"
    "ktu-web-portal-api/anon/getAttachment"
)


# ==========================================================
# Filename
# ==========================================================

def clean_filename(filename):

    if not filename:
        return "attachment.pdf"

    filename = Path(filename).name

    filename = re.sub(
        r'[<>:"/\\|?*]',
        "_",
        filename
    )

    return filename


# ==========================================================
# Decode KTU attachment response
# ==========================================================

def decode_attachment(body):

    text = body.decode(
        "utf-8",
        errors="replace"
    ).strip()

    # ------------------------------------------------------
    # JSON
    # ------------------------------------------------------

    try:

        data = json.loads(text)

        if isinstance(data, str):

            text = data

        elif isinstance(data, dict):

            for key in [
                "data",
                "file",
                "fileData",
                "dataBytes",
                "content",
                "base64"
            ]:

                value = data.get(key)

                if isinstance(value, str):

                    text = value
                    break

    except json.JSONDecodeError:

        pass

    # ------------------------------------------------------
    # Clean response
    # ------------------------------------------------------

    text = text.strip()

    if (
        len(text) >= 2
        and text[0] == '"'
        and text[-1] == '"'
    ):

        text = text[1:-1]

    # Remove data URI prefix if present

    if text.startswith("data:") and "," in text:

        text = text.split(",", 1)[1]

    # ------------------------------------------------------
    # KTU response format:
    #
    # BASE64&&filename.pdf
    #
    # Keep ONLY the part before &&
    # ------------------------------------------------------

    if "&&" in text:

        text = text.split("&&", 1)[0]

    # ------------------------------------------------------
    # Remove whitespace
    # ------------------------------------------------------

    text = re.sub(
        r"\s+",
        "",
        text
    )

    # ------------------------------------------------------
    # Remove anything that is not Base64
    # ------------------------------------------------------

    text = re.sub(
        r"[^A-Za-z0-9+/=]",
        "",
        text
    )

    # ------------------------------------------------------
    # Remove excessive trailing '='
    # ------------------------------------------------------

    text = text.rstrip("=")

    # ------------------------------------------------------
    # Add correct padding
    # ------------------------------------------------------

    remainder = len(text) % 4

    if remainder:

        text += "=" * (4 - remainder)

    print(
        f"Base64 text length: {len(text):,}"
    )

    print(
        "First 100 Base64 chars:"
    )

    print(
        repr(text[:100])
    )

    print(
        "Last 100 Base64 chars:"
    )

    print(
        repr(text[-100:])
    )

    print(
        "Base64 length:",
        len(text)
    )

    print(
        "Length % 4:",
        len(text) % 4
    )

    # ------------------------------------------------------
    # Decode
    # ------------------------------------------------------

    try:

        pdf_bytes = base64.b64decode(
            text,
            validate=True
        )

    except Exception as e:

        raise ValueError(
            f"Base64 decoding failed: {e}"
        )

    print(
        f"Decoded PDF size: "
        f"{len(pdf_bytes):,} bytes"
    )

    return pdf_bytes


# ==========================================================
# Filename from response
# ==========================================================

def get_filename_from_headers(headers):

    content_disposition = headers.get(
        "content-disposition",
        ""
    )

    match = re.search(
        r'filename="?([^";]+)"?',
        content_disposition,
        re.IGNORECASE
    )

    if match:

        return clean_filename(
            match.group(1)
        )

    return "attachment.pdf"


# ==========================================================
# Save PDF
# ==========================================================

def save_pdf(
    pdf_bytes,
    filename,
    notice_id
):

    downloads_dir = Path(
        "downloads"
    )

    downloads_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = clean_filename(
        filename
    )

    if not filename.lower().endswith(".pdf"):

        filename += ".pdf"

    output_path = (
        downloads_dir
        / f"{notice_id}_{filename}"
    )

    if output_path.exists():

        print(
            f"PDF already exists: "
            f"{output_path}"
        )

        return output_path

    with open(
        output_path,
        "wb"
    ) as file:

        file.write(pdf_bytes)

    print()
    print(
        "========== PDF SAVED =========="
    )

    print(
        f"Path: {output_path}"
    )

    print(
        f"Size: {len(pdf_bytes):,} bytes"
    )

    print(
        "==============================="
    )

    return output_path


# ==========================================================
# Download by CLICKING actual KTU notification button
# ==========================================================

def download_attachment(
    page,
    button,
    encrypt_id,
    notice_id
):

    print()
    print("Clicking KTU Notification button...")

    modify_request = None

    try:

        # --------------------------------------------------
        # Intercept the KTU attachment request BEFORE click
        # --------------------------------------------------

        def modify_request(route):

            request = route.request

            try:
                body = json.loads(
                    request.post_data or "{}"
                )

                print()
                print(
                    "Original request encryptId:",
                    body.get("encryptId")
                )

                body["encryptId"] = encrypt_id

                print(
                    "Using attachment encryptId:",
                    encrypt_id
                )

                route.continue_(
                    post_data=json.dumps(body)
                )

            except Exception as e:

                print(
                    "Could not modify attachment request:",
                    repr(e)
                )

                route.continue_()

        page.route(
            ATTACHMENT_URL,
            modify_request
        )

        # --------------------------------------------------
        # Click and capture response
        # --------------------------------------------------

        with page.expect_response(
            lambda response:
                ATTACHMENT_URL in response.url
                and response.request.method == "POST",
            timeout=15000
        ) as response_info:

            button.click()

        response = response_info.value

        # Remove route immediately after response
        page.unroute(
            ATTACHMENT_URL,
            modify_request
        )

    except Exception as e:

        print()
        print(
            "Could not capture attachment response:"
        )

        print(
            repr(e)
        )

        try:
            if modify_request:
                page.unroute(
                    ATTACHMENT_URL,
                    modify_request
                )
        except Exception:
            pass

        return None

    print()
    print(
        "========== ATTACHMENT RESPONSE =========="
    )

    print(
        "URL:",
        response.url
    )

    print(
        "Status:",
        response.status
    )

    if response.status != 200:

        body = response.body()

        print(
            "Attachment request failed."
        )

        print(
            body.decode(
                "utf-8",
                errors="replace"
            )[:1000]
        )

        return None

    body = response.body()

    print(
        f"Response size: "
        f"{len(body):,} bytes"
    )

    # ------------------------------------------------------
    # Server filename
    # ------------------------------------------------------

    filename = clean_filename(
        response.headers.get(
            "content-disposition",
            ""
        ).split("filename=", 1)[-1].strip('"')
    )

    print(
        "Filename from server:",
        filename
    )

    # ------------------------------------------------------
    # Decode
    # ------------------------------------------------------

    try:

        pdf_bytes = decode_attachment(
            body
        )

    except Exception as e:

        print(
            "Attachment decoding error:"
        )

        print(
            repr(e)
        )

        return None

    # ------------------------------------------------------
    # Verify PDF
    # ------------------------------------------------------

    if not pdf_bytes.startswith(
        b"%PDF"
    ):

        print(
            "ERROR:"
        )

        print(
            "Decoded data is not a PDF."
        )

        print(
            "First bytes:",
            repr(
                pdf_bytes[:50]
            )
        )

        return None

    print(
        "PDF signature verified!"
    )

    # ------------------------------------------------------
    # Save
    # ------------------------------------------------------

    return save_pdf(
        pdf_bytes=pdf_bytes,
        filename=filename,
        notice_id=notice_id
    )


# ==========================================================
# Main scraper
# ==========================================================

def scrape_ktu():

    print(
        "Starting KTU browser..."
    )

    cdp_url = "http://127.0.0.1:9222"

    try:
        requests.get(
            f"{cdp_url}/json/version",
            timeout=2
        )
        print("Chrome debug session already running.")

    except Exception:
        print("Chrome debug session not found.")
        print("Starting Chrome...")

        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

        profile_path = os.path.join(
            os.getcwd(),
            "chrome_debug_profile"
        )

        subprocess.Popen([
            chrome_path,
            "--remote-debugging-port=9222",
            f"--user-data-dir={profile_path}",
            KTU_ANNOUNCEMENTS_PAGE
        ])

        print("Waiting for Chrome debug session...")

        for _ in range(30):
            try:
                requests.get(
                    f"{cdp_url}/json/version",
                    timeout=2
                )
                print("Chrome debug session ready.")
                break
            except Exception:
                time.sleep(2)
        else:
            raise RuntimeError(
                "Chrome debug session could not be started."
            )

    with sync_playwright() as p:

        browser = p.chromium.connect_over_cdp(
            "http://127.0.0.1:9222"
        )

        context = browser.contexts[0]

        page = None

        for existing_page in context.pages:
            if "ktu.edu.in/Menu/announcements" in existing_page.url:
                page = existing_page
                break

        if page is None:
            page = context.new_page()
            page.goto(KTU_ANNOUNCEMENTS_PAGE)

        # page.on(
        #     "console",
        #     lambda msg: print(f"Browser console [{msg.type}]: {msg.text}")
        # )


        announcements_data = None

        # --------------------------------------------------
        # Capture announcements API
        # --------------------------------------------------

        def handle_response(response):

            nonlocal announcements_data

            if (
                ANNOUNCEMENTS_URL in response.url
                and response.request.method == "POST"
            ):
                print(f"Announcements API status: {response.status}")

                if response.status == 200:

                    try:

                        data = response.json()

                        announcements_data = data

                        print()

                        print(
                            "========== ANNOUNCEMENTS API =========="
                        )

                        print(
                            "URL:",
                            response.url
                        )

                        print(
                            "Status:",
                            response.status
                        )

                        print(
                            "Total elements:",
                            data.get(
                                "totalElements"
                            )
                        )

                        print(
                            "Number of notices:",
                            len(
                                data.get(
                                    "content",
                                    []
                                )
                            )
                        )

                    except Exception as e:

                        print(
                            "Could not parse "
                            "announcements response:",
                            e
                        )

        page.on(
            "response",
            handle_response
        )

        # --------------------------------------------------
        # Open KTU
        # --------------------------------------------------

        print(
            "Opening KTU announcements page..."
        )

        page.goto(
            KTU_ANNOUNCEMENTS_PAGE,
            wait_until="domcontentloaded",
            timeout=60000
        )

        print(
            "KTU page loaded!"
        )

        page.wait_for_timeout(
            30000
        )

        # --------------------------------------------------
        # Check announcements
        # --------------------------------------------------

        if announcements_data is None:

            print(
                "ERROR:"
            )

            print(
                "Announcements API response "
                "was not captured."
            )

            context.close()

            return None

        notices = announcements_data.get(
            "content",
            []
        )

        total_elements = announcements_data.get(
            "totalElements",
            0
        )

        print()

        print(
            "========== NOTICE PROCESSING =========="
        )

        print(
            "Total notices:",
            total_elements
        )

        print(
            "Notices received:",
            len(notices)
        )

        # --------------------------------------------------
        # Find notification buttons
        # --------------------------------------------------

        buttons = page.get_by_role(
            "button",
            name=re.compile(
                "Notification|University Order",
                re.IGNORECASE
            )
        )

        button_count = buttons.count()

        print()

        print(
            "Notification buttons found:",
            button_count
        )

        # --------------------------------------------------
        # IMPORTANT FIX
        #
        # One Notification button belongs to ONE NOTICE.
        #
        # Do NOT consume a button for every attachment.
        #
        # A notice may have multiple API attachments but
        # the KTU webpage can show only one Notification
        # button for that notice.
        # --------------------------------------------------

        # --------------------------------------------------
        # MASTER TRIGGER APPROACH
        # Since we intercept the network request and inject 
        # the exact encryptId, we don't need to map buttons.
        # We just use the first button on the page as a trigger!
        # --------------------------------------------------
        
        results = []

        master_trigger = buttons.first if button_count > 0 else None

        for index, notice in enumerate(notices, start=1):

            notice_id = notice.get("id")
            date = notice.get("announcementDate")
            subject = notice.get("subject")
            attachments = notice.get("attachmentList", [])

            print()
            print("----------------------------------------")
            print(f"NOTICE {index}/{len(notices)}")
            print("ID:", notice_id)
            print("Date:", date)
            print("Subject:", subject)
            print("Attachments:", len(attachments))

            notice_result = {
                "id": notice_id,
                "date": date,
                "subject": subject,
                "attachments": []
            }

            if not attachments:
                print("No attachments for this notice.")
                results.append(notice_result)
                continue

            if master_trigger is None:
                print("No Notification buttons available on page to trigger downloads.")
                for attachment in attachments:
                    notice_result["attachments"].append({
                        "name": attachment.get("attachmentName"),
                        "encryptId": attachment.get("encryptId"),
                        "path": None
                    })
                results.append(notice_result)
                continue

            # Download ALL attachments using the master trigger
            for attachment_index, attachment in enumerate(attachments, start=1):
                
                attachment_name = attachment.get("attachmentName")
                encrypt_id = attachment.get("encryptId")

                print()
                print(f"Attachment {attachment_index}/{len(attachments)}")
                print("Name:", attachment_name)
                print("encryptId:", encrypt_id)

                path = download_attachment(
                    page=page,
                    button=master_trigger,
                    encrypt_id=encrypt_id,
                    notice_id=notice_id
                )

                notice_result["attachments"].append({
                    "name": attachment_name,
                    "encryptId": encrypt_id,
                    "path": str(path) if path else None
                })

            results.append(notice_result)

            continue

            button = buttons.first

            # Consume exactly ONE button for this notice.

            button_index += 1

            # --------------------------------------------------
            # Download ALL attachments for this notice.
            #
            # KTU provides one button for each attachment.
            # --------------------------------------------------

            for attachment_index, attachment in enumerate(
                attachments,
                start=1
            ):

                if button_index >= button_count:

                    print(
                        "No Notification/University Order button "
                        "available for this attachment."
                    )

                    notice_result[
                        "attachments"
                    ].append(
                        {
                            "name":
                                attachment.get(
                                    "attachmentName"
                                ),
                            "encryptId":
                                attachment.get(
                                    "encryptId"
                                ),
                            "path":
                                None
                        }
                    )

                    continue

                button = page.get_by_role(
                    "button",
                    name=re.compile(
                        "Notification|University Order",
                        re.IGNORECASE
                    )
                ).nth(button_index)

                # Consume exactly ONE button for ONE attachment.
                button_index += 1

                attachment_name = attachment.get(
                    "attachmentName"
                )

                encrypt_id = attachment.get(
                    "encryptId"
                )

                print()

                print(
                    f"Attachment {attachment_index}/"
                    f"{len(attachments)}"
                )

                print(
                    "Name:",
                    attachment_name
                )

                print(
                    "encryptId:",
                    encrypt_id
                )

                # --------------------------------------------------
                # Download
                # --------------------------------------------------

                path = download_attachment(
                    page=page,
                    button=button,
                    encrypt_id=encrypt_id,
                    notice_id=notice_id
                )

                notice_result[
                    "attachments"
                ].append(
                    {
                        "name":
                            attachment_name,
                        "encryptId":
                            encrypt_id,
                        "path":
                            str(path)
                            if path
                            else None
                    }
                )

            if len(attachments) > 1:

                print()

                print(
                    f"Additional API attachments: "
                    f"{len(attachments) - 1}"
                )

                for extra_attachment in attachments[1:]:

                    notice_result[
                        "attachments"
                    ].append(
                        {
                            "name":
                                extra_attachment.get(
                                    "attachmentName"
                                ),
                            "encryptId":
                                extra_attachment.get(
                                    "encryptId"
                                ),
                            "path":
                                None
                        }
                    )

            results.append(
                notice_result
            )

        # --------------------------------------------------
        # Summary
        # --------------------------------------------------

        downloaded = sum(
            1
            for notice in results
            for attachment in notice[
                "attachments"
            ]
            if attachment["path"]
        )

        expected = sum(
            len(
                notice.get(
                    "attachmentList",
                    []
                )
            )
            for notice in notices
        )

        print()

        print(
            "========== KTU SCRAPER COMPLETE =========="
        )

        print(
            f"Notices processed: "
            f"{len(notices)}"
        )

        print(
            f"Attachments downloaded: "
            f"{downloaded}/{expected}"
        )

        print(
            "==========================================="
        )

        browser.close()

        print(
            "Browser closed."
        )

        return {
            "totalElements":
                total_elements,
            "notices":
                results
        }


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    result = scrape_ktu()

    print()

    if result:

        print(
            "KTU scraping successful."
        )

        print(
            "Total notices:",
            result["totalElements"]
        )

        print(
            "Notices received:",
            len(
                result["notices"]
            )
        )

    else:

        print(
            "KTU scraping failed."
        )