"""Unit tests for the ingestion pipeline."""

from pathlib import Path

from svearag.ingestion.chunker import RecursiveTokenChunker
from svearag.ingestion.pipeline import IngestionPipeline


def test_ingestion_pipeline_with_real_corpus(tmp_path: Path):
    raw_dir = Path(__file__).resolve().parent.parent / "data" / "raw"
    processed_dir = tmp_path / "processed"

    pipeline = IngestionPipeline(
        raw_dir=raw_dir,
        processed_dir=processed_dir,
        chunker=RecursiveTokenChunker(chunk_size=300, chunk_overlap=30),
    )

    docs, chunks = pipeline.run()

    assert len(docs) >= 5
    assert len(chunks) >= 10
    assert (processed_dir / "chunks.json").exists()

    # Verify chunk structure
    assert chunks[0].chunk_id is not None
    assert chunks[0].document_id is not None
    assert chunks[0].text is not None
    assert chunks[0].metadata.agency in {"Migrationsverket", "Skatteverket"}


def test_ingestion_pipeline_empty_dir(tmp_path: Path):
    empty_raw = tmp_path / "empty_raw"
    empty_raw.mkdir()
    pipeline = IngestionPipeline(raw_dir=empty_raw, processed_dir=tmp_path / "proc")
    docs, chunks = pipeline.run()

    assert docs == []
    assert chunks == []
