"""
Loads supported files from the datasets directory and converts their contents into plain text while preserving the source filename for later chunking and retrieval.

Example:
datasets/company.txt -> LoadedDocument(text="Company information...", source="company.txt")
"""

import csv
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from pypdf import PdfReader


@dataclass
class LoadedDocument:
    text: str
    source: str


def _load_csv(path: Path) -> str:
    rows_text = []

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            row_text = ", ".join(
                f"{key}: {value}"
                for key, value in row.items()
                if value
            )

            if row_text:
                rows_text.append(row_text)

    return "\n".join(rows_text)


def _load_pdf(path: Path) -> str:
    reader = PdfReader(path)

    pages_text = [
        page.extract_text().strip()
        for page in reader.pages
        if page.extract_text()
    ]

    return "\n\n".join(pages_text)


def _load_text(path: Path) -> str:
    return path.read_text(
        encoding="utf-8",
        errors="ignore"
    )


_LOADERS: dict[str, Callable[[Path], str]] = {
    ".csv": _load_csv,
    ".pdf": _load_pdf,
    ".txt": _load_text,
    ".md": _load_text,
}


def load_documents(datasets_dir: Path) -> list[LoadedDocument]:
    """Walkthru the datasets directory 'recursively' and load every supported file into text"""
    documents = []

    for path in sorted(datasets_dir.rglob("*")):

        if not path.is_file():
            continue

        loader = _LOADERS.get(path.suffix.lower())

        if loader is None:
            continue

        try:
            text = loader(path).strip()
        except Exception as error:
            print(f"Failed to load {path}: {error}")
            continue

        if text:
            documents.append(
                LoadedDocument(
                    text=text,
                    source=str(path.relative_to(datasets_dir))
                )
            )

    return documents
