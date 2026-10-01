"""Ingestion pipeline orchestrating document loading, chunking, and persistence."""

import json
from pathlib import Path

from svearag.core.logging import logger
from svearag.core.models import Chunk, Document
from svearag.ingestion.chunker import BaseChunker, RecursiveTokenChunker
from svearag.ingestion.loader import DirectoryDocumentLoader


class IngestionPipeline:
    """Orchestrates loading, cleaning, chunking, and storing corpus documents."""

    def __init__(
        self,
        raw_dir: Path | str,
        processed_dir: Path | str | None = None,
        chunker: BaseChunker | None = None,
    ) -> None:
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir) if processed_dir else None
        self.chunker = chunker or RecursiveTokenChunker(chunk_size=350, chunk_overlap=50)

    def run(self) -> tuple[list[Document], list[Chunk]]:
        """Executes full loading and chunking pipeline.

        Returns:
            Tuple of (loaded_documents, generated_chunks).
        """
        logger.info("Starting ingestion pipeline", extra_data={"raw_dir": str(self.raw_dir)})

        loader = DirectoryDocumentLoader(self.raw_dir)
        documents = loader.load()

        if not documents:
            logger.warning(
                "No documents found in raw directory", extra_data={"dir": str(self.raw_dir)}
            )
            return [], []

        chunks = self.chunker.chunk_documents(documents)

        # Save processed chunks to disk if processed_dir is configured
        if self.processed_dir:
            self.processed_dir.mkdir(parents=True, exist_ok=True)
            output_file = self.processed_dir / "chunks.json"
            chunk_data = [chunk.model_dump() for chunk in chunks]
            output_file.write_text(
                json.dumps(chunk_data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            logger.info(
                "Saved processed chunks",
                extra_data={"chunks_count": len(chunks), "output_file": str(output_file)},
            )

        logger.info(
            "Ingestion pipeline completed",
            extra_data={"docs_count": len(documents), "chunks_count": len(chunks)},
        )
        return documents, chunks
