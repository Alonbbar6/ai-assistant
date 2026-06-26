from pathlib import Path


def extract_pdf_text(path: str, max_pages: int = 50) -> str:
    """Extract text from a PDF file."""
    try:
        import pdfplumber
    except ImportError:
        return "pdfplumber not installed. Run: pip install pdfplumber"

    path = Path(path)
    if not path.exists():
        return f"File not found: {path}"

    pages_text = []
    try:
        with pdfplumber.open(path) as pdf:
            total = len(pdf.pages)
            for i, page in enumerate(pdf.pages[:max_pages]):
                text = page.extract_text() or ""
                if text.strip():
                    pages_text.append(f"--- Page {i+1} ---\n{text.strip()}")
            suffix = f"\n\n[Document has {total} pages total]" if total > max_pages else ""
            return "\n\n".join(pages_text) + suffix
    except Exception as e:
        return f"Failed to read PDF: {e}"


def get_pdf_metadata(path: str) -> dict:
    """Return PDF metadata (title, author, page count)."""
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            meta = pdf.metadata or {}
            return {
                "pages": len(pdf.pages),
                "title": meta.get("Title", ""),
                "author": meta.get("Author", ""),
                "subject": meta.get("Subject", ""),
            }
    except Exception as e:
        return {"error": str(e)}
