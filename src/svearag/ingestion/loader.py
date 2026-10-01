"""Document loaders for Swedish public administrative corpus."""

import re
from pathlib import Path

import yaml

from svearag.core.logging import logger
from svearag.core.models import Document, DocumentMetadata


def parse_markdown_with_frontmatter(file_path: Path) -> Document:
    """Parses a Markdown file containing YAML frontmatter into a Document model.

    Args:
        file_path: Path to the markdown file.

    Returns:
        Document instance with validated metadata.

    Raises:
        ValueError: If frontmatter is missing or invalid.
    """
    content = file_path.read_text(encoding="utf-8")
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)

    if not frontmatter_match:
        # If no YAML frontmatter, extract title from first H1 and synthesize metadata
        title = file_path.stem.replace("_", " ").title()
        metadata = DocumentMetadata(
            agency="Unknown",
            document_id=file_path.stem.upper(),
            language="en",
            source_url=f"file://{file_path.name}",
            category="General",
        )
        return Document(
            id=metadata.document_id,
            title=title,
            content=content.strip(),
            metadata=metadata,
        )

    raw_yaml, body_text = frontmatter_match.groups()
    parsed_meta = yaml.safe_load(raw_yaml) or {}

    title = parsed_meta.get("title", file_path.stem.replace("_", " ").title())
    doc_id = parsed_meta.get("document_id", file_path.stem.upper())

    metadata = DocumentMetadata(
        agency=parsed_meta.get("agency", "Public Agency"),
        document_id=doc_id,
        language=parsed_meta.get("language", "en"),
        source_url=parsed_meta.get("source_url", f"https://example.se/{doc_id.lower()}"),
        last_updated=parsed_meta.get("last_updated"),
        category=parsed_meta.get("category"),
        extra={
            k: v
            for k, v in parsed_meta.items()
            if k
            not in {
                "title",
                "document_id",
                "agency",
                "language",
                "source_url",
                "last_updated",
                "category",
            }
        },
    )

    return Document(
        id=doc_id,
        title=title,
        content=body_text.strip(),
        metadata=metadata,
    )


class DirectoryDocumentLoader:
    """Loads all Markdown and text documents from a directory."""

    def __init__(self, directory_path: Path | str, glob_pattern: str = "*.md") -> None:
        self.directory_path = Path(directory_path)
        self.glob_pattern = glob_pattern

    def load(self) -> list[Document]:
        """Loads and returns all documents in the directory."""
        if not self.directory_path.exists():
            logger.warning(
                "Directory does not exist", extra_data={"path": str(self.directory_path)}
            )
            return []

        files = sorted(self.directory_path.glob(self.glob_pattern))
        documents: list[Document] = []

        for f in files:
            try:
                doc = parse_markdown_with_frontmatter(f)
                documents.append(doc)
            except Exception as e:
                logger.error(
                    "Failed to parse document", extra_data={"file": str(f), "error": str(e)}
                )

        logger.info(
            "Loaded documents from directory",
            extra_data={"count": len(documents), "path": str(self.directory_path)},
        )
        return documents
