"""Load knowledge documents from the datasets directory."""

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".md",
}


@dataclass(frozen=True)
class LoadedDocument:
    """A document loaded from the knowledge base."""

    text: str
    source: str


def _load_pdf(path: Path) -> str:
    """Extract text from a PDF."""

    reader = PdfReader(path)

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):
        text = page.extract_text()

        if not text:
            continue

        pages.append(
            f"[Page {page_number}]\n{text.strip()}"
        )

    return "\n\n".join(pages)


def _load_text(path: Path) -> str:
    """Load plain text or Markdown."""

    return path.read_text(
        encoding="utf-8"
    )


def _load_file(path: Path) -> str:
    """Load one supported knowledge document."""

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _load_pdf(path)

    if suffix in {".txt", ".md"}:
        return _load_text(path)

    raise ValueError(
        f"Unsupported file type: {path}"
    )


def load_documents(
    dataset_dir: Path,
) -> list[LoadedDocument]:
    """Load every supported document recursively."""

    documents = []

    for path in sorted(
        dataset_dir.rglob("*")
    ):
        if not path.is_file():
            continue

        if (
            path.suffix.lower()
            not in SUPPORTED_EXTENSIONS
        ):
            continue

        try:
            text = _load_file(path).strip()

        except Exception as error:
            raise RuntimeError(
                f"Failed to load {path}"
            ) from error

        if not text:
            continue

        source = str(
            path.relative_to(dataset_dir)
        )

        documents.append(
            LoadedDocument(
                text=text,
                source=source,
            )
        )

    return documents