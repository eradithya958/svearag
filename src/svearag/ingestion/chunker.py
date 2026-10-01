"""Chunking strategies for document segmentation with metadata preservation."""

from abc import ABC, abstractmethod

from svearag.core.models import Chunk, Document


class BaseChunker(ABC):
    """Abstract base class for document chunkers."""

    @abstractmethod
    def chunk_document(self, document: Document) -> list[Chunk]:
        """Splits a single document into a list of chunks."""
        pass

    def chunk_documents(self, documents: list[Document]) -> list[Chunk]:
        """Splits multiple documents into a flat list of chunks."""
        all_chunks: list[Chunk] = []
        for doc in documents:
            all_chunks.extend(self.chunk_document(doc))
        return all_chunks


def approximate_token_count(text: str) -> int:
    """Estimates token count using whitespace and punctuation heuristics (~1.3 words/token)."""
    words = len(text.split())
    return max(1, int(words * 1.3))


class RecursiveTokenChunker(BaseChunker):
    """Chunks documents using hierarchical separators with configurable size and overlap."""

    def __init__(
        self,
        chunk_size: int = 350,
        chunk_overlap: int | None = None,
        separators: list[str] | None = None,
    ) -> None:
        if chunk_overlap is None:
            chunk_overlap = min(50, max(0, int(chunk_size * 0.15)))
        elif chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be strictly less than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " "]

    def _split_text(self, text: str, separators: list[str]) -> list[str]:
        """Recursively splits text into segments smaller than chunk_size."""
        if not separators or approximate_token_count(text) <= self.chunk_size:
            return [text.strip()] if text.strip() else []

        sep = separators[0]
        splits = text.split(sep)
        result: list[str] = []
        current_chunk: list[str] = []
        current_tokens = 0

        for split in splits:
            split_trimmed = split.strip()
            if not split_trimmed:
                continue

            split_tokens = approximate_token_count(split_trimmed)
            if split_tokens > self.chunk_size and len(separators) > 1:
                # Recursively subdivide with next separator
                sub_splits = self._split_text(split_trimmed, separators[1:])
                for sub in sub_splits:
                    sub_tok = approximate_token_count(sub)
                    if current_tokens + sub_tok > self.chunk_size and current_chunk:
                        result.append(sep.join(current_chunk).strip())
                        # Keep overlap if possible
                        current_chunk = [sub]
                        current_tokens = sub_tok
                    else:
                        current_chunk.append(sub)
                        current_tokens += sub_tok
            else:
                if current_tokens + split_tokens > self.chunk_size and current_chunk:
                    result.append(sep.join(current_chunk).strip())
                    current_chunk = [split_trimmed]
                    current_tokens = split_tokens
                else:
                    current_chunk.append(split_trimmed)
                    current_tokens += split_tokens

        if current_chunk:
            result.append(sep.join(current_chunk).strip())

        return result

    def chunk_document(self, document: Document) -> list[Chunk]:
        """Splits document content into chunks with sequential chunk IDs and metadata."""
        raw_segments = self._split_text(document.content, self.separators)
        chunks: list[Chunk] = []

        for idx, seg in enumerate(raw_segments):
            chunk_id = f"{document.id}_c{idx:03d}"
            token_cnt = approximate_token_count(seg)
            chunk = Chunk(
                chunk_id=chunk_id,
                document_id=document.id,
                text=seg,
                chunk_index=idx,
                token_count=token_cnt,
                metadata=document.metadata,
            )
            chunks.append(chunk)

        return chunks


class SemanticHeaderChunker(BaseChunker):
    """Splits Markdown documents by headers (#, ##, ###) preserving section lineage."""

    def __init__(self, max_chunk_size: int = 500) -> None:
        self.max_chunk_size = max_chunk_size

    def chunk_document(self, document: Document) -> list[Chunk]:
        lines = document.content.split("\n")
        sections: list[tuple[str, str]] = []  # (header, content)
        current_header = document.title
        current_lines: list[str] = []

        for line in lines:
            if line.startswith("#"):
                if current_lines:
                    sections.append((current_header, "\n".join(current_lines).strip()))
                    current_lines = []
                current_header = line.lstrip("#").strip()
            else:
                current_lines.append(line)

        if current_lines:
            sections.append((current_header, "\n".join(current_lines).strip()))

        chunks: list[Chunk] = []
        for idx, (hdr, sec_text) in enumerate(sections):
            if not sec_text:
                continue
            full_chunk_text = f"## {hdr}\n{sec_text}" if hdr != document.title else sec_text
            chunk = Chunk(
                chunk_id=f"{document.id}_sec_{idx:03d}",
                document_id=document.id,
                text=full_chunk_text,
                chunk_index=idx,
                token_count=approximate_token_count(full_chunk_text),
                metadata=document.metadata,
            )
            chunks.append(chunk)

        return chunks
