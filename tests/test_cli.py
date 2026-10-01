"""Unit tests for SveaRAG CLI commands."""

from pathlib import Path
from unittest.mock import patch

from svearag.cli import main, run_ingest


def test_cli_run_ingest(tmp_path: Path):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "doc1.md").write_text(
        "---\ntitle: 'Doc'\nagency: 'A'\ndocument_id: 'D1'\nsource_url: 'u1'\n---\nHello world"
    )
    processed = tmp_path / "proc"

    run_ingest(raw_dir=raw, processed_dir=processed)
    assert (processed / "chunks.json").exists()


def test_cli_main_dispatch(tmp_path: Path):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "doc1.md").write_text(
        "---\ntitle: 'Doc'\nagency: 'A'\ndocument_id: 'D1'\nsource_url: 'u1'\n---\nHello world"
    )
    processed = tmp_path / "proc"

    with patch(
        "sys.argv", ["svearag", "ingest", "--raw-dir", str(raw), "--processed-dir", str(processed)]
    ):
        main()

    assert (processed / "chunks.json").exists()
