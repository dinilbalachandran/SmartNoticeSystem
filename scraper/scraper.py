from scraper.notice_parser import extract_text_from_pdf
import os
import base64
import json
import re
from pathlib import Path

import requests


# --------------------------------------------------
# KTU API configuration
# --------------------------------------------------

KTU_API_BASE = "https://api.ktu.edu.in/ktu-web-portal-api/anon"

ANNOUNCEMENTS_URL = f"{KTU_API_BASE}/announcemnts"
ATTACHMENT_URL = f"{KTU_API_BASE}/getAttachment"

KTU_TOKEN = os.getenv("KTU_API_TOKEN")


# --------------------------------------------------
# Headers
# --------------------------------------------------

def get_headers():
    if not KTU_TOKEN:
        raise RuntimeError(
            "KTU_API_TOKEN environment variable is not set."
        )

    return {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://ktu.edu.in",
        "Referer": "https://ktu.edu.in/",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        ),
        "x-Token": KTU_TOKEN,
    }


# --------------------------------------------------
# Get notices
# --------------------------------------------------

def get_notices():

    print("Connecting to KTU API...")

    payload = {
        "number": 0,
        "searchText": "",
        "size": 10
    }

    try:
        response = requests.post(
            ANNOUNCEMENTS_URL,
            headers=get_headers(),
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        print("KTU API connection successful!")

        return data

    except requests.RequestException as e:

        print(f"KTU API Error: {e}")

        if hasattr(e, "response") and e.response is not None:
            print("Status:", e.response.status_code)
            print("Response:", e.response.text[:1000])

        return None


# --------------------------------------------------
# Extract notice list
# --------------------------------------------------

def extract_notice_list(data):

    print("\n========== API RESPONSE KEYS ==========")

    if isinstance(data, dict):
        print(data.keys())

    print("=======================================\n")

    if not isinstance(data, dict):
        return []

    # Try common response structures

    if isinstance(data.get("content"), list):
        return data["content"]

    if isinstance(data.get("data"), list):
        return data["data"]

    if isinstance(data.get("data"), dict):

        if isinstance(data["data"].get("content"), list):
            return data["data"]["content"]

        if isinstance(data["data"].get("data"), list):
            return data["data"]["data"]

    return []


# --------------------------------------------------
# Clean filename
# --------------------------------------------------

def clean_filename(filename):

    if not filename:
        return "attachment.pdf"

    filename = Path(filename).name

    # Remove characters that are unsafe in Windows filenames
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)

    return filename


# --------------------------------------------------
# Decode PDF response
# --------------------------------------------------

def decode_pdf_response(response):

    # The endpoint may return:
    #
    # 1. raw Base64 text
    # 2. JSON containing a Base64 string
    # 3. a JSON string containing Base64
    #
    # So we handle all three.

    text = response.text.strip()

    # Try JSON first
    try:
        data = response.json()

        if isinstance(data, str):
            text = data

        elif isinstance(data, dict):

            # Possible field names
            for key in [
                "data",
                "file",
                "fileData",
                "dataBytes",
                "content",
                "base64"
            ]:
                if key in data and isinstance(data[key], str):
                    text = data[key]
                    break

    except ValueError:
        # Not JSON; use response.text directly
        pass

    # Remove quotes if the API returned a JSON string
    text = text.strip().strip('"')

    # Remove data URI prefix if present
    if "," in text and text.startswith("data:"):
        text = text.split(",", 1)[1]

    # Remove whitespace/newlines from Base64
    text = re.sub(r"\s+", "", text)

    try:
        return base64.b64decode(text, validate=False)

    except Exception as e:
        raise ValueError(
            f"Could not decode attachment as Base64: {e}"
        )


# --------------------------------------------------
# Download one attachment
# --------------------------------------------------

def download_attachment(encrypt_id, filename, notice_id):

    if not encrypt_id:
        print("No encryptId found.")
        return None

    payload = {
        "encryptId": encrypt_id
    }

    print(f"Downloading attachment for notice {notice_id}...")

    try:

        response = requests.post(
            ATTACHMENT_URL,
            headers=get_headers(),
            json=payload,
            timeout=60
        )

        response.raise_for_status()

        pdf_bytes = decode_pdf_response(response)

        if not pdf_bytes.startswith(b"%PDF"):
            print("Warning: downloaded data does not start with %PDF.")

        # Create downloads directory
        downloads_dir = Path("downloads")
        downloads_dir.mkdir(exist_ok=True)

        safe_filename = clean_filename(filename)

        # Make sure the file has .pdf extension
        if not safe_filename.lower().endswith(".pdf"):
            safe_filename += ".pdf"

        # Add notice ID to avoid filename conflicts
        output_filename = f"{notice_id}_{safe_filename}"

        output_path = downloads_dir / output_filename

        # Don't download the same PDF again
        if output_path.exists():
            print(f"PDF already exists: {output_path}")

            text = extract_text_from_pdf(output_path)

            print(f"Extracted text: {len(text):,} characters")

            return output_path

        with open(output_path, "wb") as file:
            file.write(pdf_bytes)

        print(f"PDF saved: {output_path}")
        print(f"PDF size: {len(pdf_bytes):,} bytes")

        text = extract_text_from_pdf(output_path)

        print(f"Extracted text: {len(text):,} characters")

        return output_path

    except requests.RequestException as e:

        print(f"Attachment API Error: {e}")

        if hasattr(e, "response") and e.response is not None:
            print("Status:", e.response.status_code)
            print("Response:", e.response.text[:500])

        return None

    except Exception as e:

        print(f"Attachment processing error: {e}")

        return None


# --------------------------------------------------
# Process notices
# --------------------------------------------------

def process_notices():

    data = get_notices()

    if not data:
        print("Could not retrieve notices from KTU.")
        return

    notices = extract_notice_list(data)

    print(f"Total notices: {data.get('totalElements', 'Unknown')}")
    print(f"Notices received: {len(notices)}")
    print()

    if not notices:
        print("No notices found.")
        return

    # --------------------------------------------------
    # Show first notice raw data
    # --------------------------------------------------

    print("========== FIRST NOTICE RAW DATA ==========")
    print(json.dumps(notices[0], indent=4, ensure_ascii=False))
    print("===========================================")
    print()

    # --------------------------------------------------
    # Process every notice
    # --------------------------------------------------

    for notice in notices:

        notice_id = notice.get("id")
        subject = notice.get("subject")
        announcement_date = notice.get("announcementDate")

        print("--------------------------------")
        print(f"ID: {notice_id}")
        print(f"Date: {announcement_date}")
        print(f"Subject: {subject}")

        attachments = notice.get("attachmentList", [])

        if not attachments:
            print("Attachment: None")
            print("--------------------------------")
            continue

        print(f"Attachments: {len(attachments)}")

        for attachment in attachments:

            encrypt_id = attachment.get("encryptId")
            filename = attachment.get("attachmentName")

            print(f"Attachment name: {filename}")
            print(f"encryptId: {encrypt_id}")

            download_attachment(
                encrypt_id=encrypt_id,
                filename=filename,
                notice_id=notice_id
            )

        print("--------------------------------")


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":
    process_notices()