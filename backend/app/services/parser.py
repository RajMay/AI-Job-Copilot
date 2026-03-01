import os
from pypdf import PdfReader  # ✅ pypdf is the maintained fork of PyPDF2
from docx import Document


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to read PDF: {e}")


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a .docx Word file."""
    try:
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        raise ValueError(f"Failed to read DOCX: {e}")


def extract_text_from_txt(file_path: str) -> str:
    """Extract text from a plain .txt file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except UnicodeDecodeError:
        # ✅ Fallback encoding for non-UTF-8 files
        with open(file_path, "r", encoding="latin-1") as f:
            return f.read().strip()
    except Exception as e:
        raise ValueError(f"Failed to read TXT: {e}")


def extract_text(file_path: str) -> str:
    """
    Extract text from a resume file.
    Supports: .pdf, .docx, .txt
    """

    # ✅ Check file exists before processing
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # ✅ Check file is not empty
    if os.path.getsize(file_path) == 0:
        raise ValueError(f"File is empty: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: '{ext}'. Supported: .pdf, .docx, .txt")