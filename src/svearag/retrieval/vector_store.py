"""Vector store abstractions and Qdrant implementation."""

from abc import ABC, abstractmethod
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from svearag.core.logging import logger
from svearag.core.models import Chunk, DocumentMetadata, SearchResult


class VectorStore(ABC):
    """Abstract interface for vector database storage and similarity search."""

    @abstractmethod
    def create_collection(
        self, collection_name: str, vector_size: int, recreate: bool = False
    ) -> None:
        """Initializes or resets a vector collection."""
        pass

    @abstractmethod
    def upsert_chunks(
        self,
        collection_name: str,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> int:
        """Upserts chunks and their vector embeddings into the collection."""
        pass

    @abstractmethod
    def search(
        self,
        collection_name: str,
        query_vector: list[float],
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """Performs approximate nearest neighbor search."""
        pass


class QdrantVectorStore(VectorStore):
    """Qdrant vector store adapter supporting both in-memory and networked client."""

    def __init__(
        self,
        client: QdrantClient | None = None,
        in_memory: bool = True,
        host: str = "localhost",
        port: int = 6333,
        url: str | None = None,
    ) -> None:
        if client is not None:
            self.client = client
        elif in_memory:
            self.client = QdrantClient(location=":memory:")
        elif url:
            self.client = QdrantClient(url=url)
        else:
            self.client = QdrantClient(host=host, port=port)

    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        recreate: bool = False,
    ) -> None:
        collections = [c.name for c in self.client.get_collections().collections]
        if collection_name in collections:
            if recreate:
                self.client.delete_collection(collection_name=collection_name)
            else:
                return

        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=qmodels.VectorParams(
                size=vector_size,
                distance=qmodels.Distance.COSINE,
            ),
        )
        logger.info(
            "Created Qdrant collection",
            extra_data={"collection": collection_name, "vector_size": vector_size},
        )

    def upsert_chunks(
        self,
        collection_name: str,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> int:
        if len(chunks) != len(embeddings):
            raise ValueError(f"Chunk count ({len(chunks)}) != embedding count ({len(embeddings)})")

        if not chunks:
            return 0

        points: list[qmodels.PointStruct] = []
        for idx, (chunk, emb) in enumerate(zip(chunks, embeddings, strict=True)):
            point_id = idx  # or integer hash / UUID
            payload = {
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "text": chunk.text,
                "chunk_index": chunk.chunk_index,
                "token_count": chunk.token_count,
                "agency": chunk.metadata.agency,
                "language": chunk.metadata.language,
                "source_url": chunk.metadata.source_url,
                "last_updated": chunk.metadata.last_updated,
                "category": chunk.metadata.category,
                "extra": chunk.metadata.extra,
            }
            points.append(
                qmodels.PointStruct(
                    id=point_id,
                    vector=emb,
                    payload=payload,
                )
            )

        self.client.upsert(collection_name=collection_name, points=points)
        logger.info(
            "Upserted chunks to Qdrant",
            extra_data={"collection": collection_name, "count": len(points)},
        )
        return len(points)

    def search(
        self,
        collection_name: str,
        query_vector: list[float],
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        qdrant_filter = None
        if filters:
            must_conditions = []
            for key, val in filters.items():
                if val is not None:
                    must_conditions.append(
                        qmodels.FieldCondition(key=key, match=qmodels.MatchValue(value=val))
                    )
            if must_conditions:
                qdrant_filter = qmodels.Filter(must=must_conditions)

        if hasattr(self.client, "query_points"):
            query_res = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=top_k,
                query_filter=qdrant_filter,
            )
            hits = query_res.points
        else:  # pragma: no cover
            hits = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k,
                query_filter=qdrant_filter,
            )

        results: list[SearchResult] = []
        for rank, hit in enumerate(hits, start=1):
            payload = hit.payload or {}
            metadata = DocumentMetadata(
                agency=payload.get("agency", "Unknown"),
                document_id=payload.get("document_id", "DOC"),
                language=payload.get("language", "en"),
                source_url=payload.get("source_url", ""),
                last_updated=payload.get("last_updated"),
                category=payload.get("category"),
                extra=payload.get("extra", {}),
            )
            chunk = Chunk(
                chunk_id=payload.get("chunk_id", f"c_{hit.id}"),
                document_id=payload.get("document_id", "DOC"),
                text=payload.get("text", ""),
                chunk_index=payload.get("chunk_index", 0),
                token_count=payload.get("token_count", 0),
                metadata=metadata,
            )
            results.append(
                SearchResult(
                    chunk=chunk,
                    score=float(hit.score),
                    retrieval_type="dense",
                    rank=rank,
                )
            )

        return results
