"""Unit tests for document loading and Markdown frontmatter parsing."""

from pathlib import Path

from svearag.ingestion.loader import DirectoryDocumentLoader, parse_markdown_with_frontmatter


def test_parse_markdown_with_frontmatter(tmp_path: Path):
    doc_path = tmp_path / "test_doc.md"
    doc_path.write_text(
        "---\n"
        "title: 'Test Guide'\n"
        "agency: 'Migrationsverket'\n"
        "document_id: 'MV-TEST-001'\n"
        "language: 'en'\n"
        "source_url: 'https://example.com/guide'\n"
        "category: 'Immigration'\n"
        "---\n\n"
        "# Test Guide Header\n\n"
        "This is sample body content.",
        encoding="utf-8",
    )

    doc = parse_markdown_with_frontmatter(doc_path)
    assert doc.id == "MV-TEST-001"
    assert doc.title == "Test Guide"
    assert doc.metadata.agency == "Migrationsverket"
    assert doc.metadata.language == "en"
    assert doc.metadata.category == "Immigration"
    assert "This is sample body content." in doc.content


def test_parse_markdown_without_frontmatter(tmp_path: Path):
    doc_path = tmp_path / "plain_guide.md"
    doc_path.write_text(
        "# Plain Header\n\nBody content without YAML frontmatter.", encoding="utf-8"
    )

    doc = parse_markdown_with_frontmatter(doc_path)
    assert doc.id == "PLAIN_GUIDE"
    assert doc.metadata.agency == "Unknown"
    assert "Body content without YAML" in doc.content


def test_directory_document_loader(tmp_path: Path):
    (tmp_path / "doc1.md").write_text(
        "---\ntitle: 'Doc 1'\nagency: 'A'\ndocument_id: 'D1'\nsource_url: 'u1'\n---\nText 1"
    )
    (tmp_path / "doc2.md").write_text(
        "---\ntitle: 'Doc 2'\nagency: 'B'\ndocument_id: 'D2'\nsource_url: 'u2'\n---\nText 2"
    )
    (tmp_path / "ignored.txt").write_text("Ignore me")

    loader = DirectoryDocumentLoader(tmp_path, glob_pattern="*.md")
    docs = loader.load()

    assert len(docs) == 2
    assert {d.id for d in docs} == {"D1", "D2"}


def test_directory_document_loader_nonexistent():
    loader = DirectoryDocumentLoader("/nonexistent/directory/path/123")
    docs = loader.load()
    assert docs == []
