"""Command Line Interface for SveaRAG ingestion and testing."""

import argparse
from pathlib import Path

from svearag.core.config import get_settings
from svearag.ingestion.chunker import RecursiveTokenChunker
from svearag.ingestion.pipeline import IngestionPipeline


def run_ingest(raw_dir: Path | None = None, processed_dir: Path | None = None) -> None:
    """Executes corpus ingestion and outputs chunk stats."""
    settings = get_settings()
    raw = raw_dir or settings.raw_data_dir
    processed = processed_dir or settings.processed_data_dir

    print(f"📦 Indexing documents from: {raw}")
    pipeline = IngestionPipeline(
        raw_dir=raw,
        processed_dir=processed,
        chunker=RecursiveTokenChunker(
            chunk_size=settings.default_chunk_size,
            chunk_overlap=settings.default_chunk_overlap,
        ),
    )

    docs, chunks = pipeline.run()

    print("\n✅ Ingestion Succeeded!")
    print(f"  • Total Documents Loaded: {len(docs)}")
    print(f"  • Total Chunks Generated: {len(chunks)}")
    print(f"  • Output Directory: {processed}")
    print("\nDocument Breakdown:")
    for d in docs:
        print(f"  - [{d.metadata.agency}] ({d.metadata.language.upper()}) {d.title} (ID: {d.id})")


def main() -> None:
    """CLI entrypoint dispatcher."""
    parser = argparse.ArgumentParser(description="SveaRAG CLI tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Run document ingestion and chunking")
    ingest_parser.add_argument(
        "--raw-dir", type=Path, default=None, help="Path to raw markdown docs"
    )
    ingest_parser.add_argument(
        "--processed-dir", type=Path, default=None, help="Path to processed chunks"
    )

    args = parser.parse_args()

    if args.command == "ingest":
        run_ingest(raw_dir=args.raw_dir, processed_dir=args.processed_dir)


if __name__ == "__main__":
    main()
