import io
from pypdf import PdfReader


def extract_text_from_pdf_bytes(pdf_bytes):
    all_text = ""
    with io.BytesIO(pdf_bytes) as pdf_stream:
        reader = PdfReader(pdf_stream)
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text:
                all_text += f"--- Page {page_num} ---\n{text}\n"
    return all_text

# Example usage:

if __name__ == "__main__":
    pdf_file_path = "path/to/your/pdf/file.pdf"
    with open(pdf_file_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()

    extracted_text = extract_text_from_pdf_bytes(pdf_bytes)
    print(extracted_text)