from pathlib import Path
from pypdf import PdfReader


def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        return ""

    try:
        reader = PdfReader(pdf_path)

        pages = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                pages.append(text)

        return "\n".join(pages)

    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""


def parse_notice_pdf(pdf_path):
    """
    Extract and display the text from a notice PDF.
    """

    print("--------------------------------")
    print(f"Reading PDF: {pdf_path}")

    text = extract_text_from_pdf(pdf_path)

    if not text:
        print("No text could be extracted.")
        return None

    print("PDF text extracted successfully!")
    print(f"Characters extracted: {len(text):,}")

    print("\n========== PDF TEXT ==========\n")
    print(text[:5000])
    print("\n==============================")

    return text


if __name__ == "__main__":
    # Temporary test
    pdf = Path("downloads/5421_SpotAdmission-.pdf")

    parse_notice_pdf(pdf)