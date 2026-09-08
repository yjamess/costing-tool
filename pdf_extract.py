from pathlib import Path

from pypdf import PdfReader


def extract_pdf_text(pdf_path: str | Path) -> str:
    path = Path(pdf_path)
    if not path.is_file():
        raise FileNotFoundError(f"PDF not found: {path}")

    reader = PdfReader(path)
    pages: list[str] = []

    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(f"--- Page {i} ---\n{text}")

    if not pages:
        raise ValueError(
            f"No text extracted from {path.name}. "
        )

    return "\n\n".join(pages)
