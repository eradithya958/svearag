"""Dependency injection container for FastAPI routes."""

from svearag.core.config import Settings, get_settings
from svearag.core.logging import logger
from svearag.generation.engine import RAGEngine
from svearag.generation.llm import FakeLLMClient, LLMClient, OllamaLLMClient
from svearag.generation.prompt import PromptBuilder
from svearag.ingestion.chunker import RecursiveTokenChunker
from svearag.ingestion.pipeline import IngestionPipeline
from svearag.retrieval.bm25 import BM25Index
from svearag.retrieval.embeddings import (
    EmbeddingProvider,
    MockEmbeddingProvider,
    SentenceTransformerEmbeddingProvider,
)
from svearag.retrieval.hybrid import RRFHybridRetriever
from svearag.retrieval.vector_store import QdrantVectorStore, VectorStore


class AppContainer:
    """Application dependency container holding singleton services."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

        # 1. Embedding Provider
        if self.settings.environment == "testing":
            self.embedding_provider: EmbeddingProvider = MockEmbeddingProvider(dimension=64)
        else:
            self.embedding_provider = SentenceTransformerEmbeddingProvider(
                model_name=self.settings.embedding_model_name,
                dimension=self.settings.embedding_dimension,
            )

        # 2. Vector Store
        if self.settings.use_in_memory_vector_store or self.settings.environment == "testing":
            self.vector_store: VectorStore = QdrantVectorStore(in_memory=True)
        else:
            self.vector_store = QdrantVectorStore(
                in_memory=False,
                host=self.settings.qdrant_host,
                port=self.settings.qdrant_port,
                url=self.settings.qdrant_url,
            )

        # 3. BM25 Index
        self.bm25_index = BM25Index()

        # 4. LLM Client
        if self.settings.environment == "testing":
            self.llm_client: LLMClient = FakeLLMClient()
        else:
            self.llm_client = OllamaLLMClient(model="llama3.2")

        # 5. Hybrid Retriever
        self.retriever = RRFHybridRetriever(
            embedding_provider=self.embedding_provider,
            vector_store=self.vector_store,
            bm25_index=self.bm25_index,
            collection_name=self.settings.qdrant_collection_name,
            rrf_k=self.settings.rrf_k,
        )

        # 6. RAG Engine
        self.rag_engine = RAGEngine(
            retriever=self.retriever,
            llm_client=self.llm_client,
            prompt_builder=PromptBuilder(),
        )

        self.indexed_doc_count = 0
        self.indexed_chunk_count = 0
        self.feedback_records: list[dict] = []

    def initialize_corpus(self) -> tuple[int, int]:
        """Indexes raw documents from disk into vector store and BM25 index."""
        pipeline = IngestionPipeline(
            raw_dir=self.settings.raw_data_dir,
            processed_dir=self.settings.processed_data_dir,
            chunker=RecursiveTokenChunker(
                chunk_size=self.settings.default_chunk_size,
                chunk_overlap=self.settings.default_chunk_overlap,
            ),
        )
        docs, chunks = pipeline.run()

        if chunks:
            self.vector_store.create_collection(
                collection_name=self.settings.qdrant_collection_name,
                vector_size=self.embedding_provider.dimension,
                recreate=True,
            )
            embeddings = self.embedding_provider.embed_batch([c.text for c in chunks])
            self.vector_store.upsert_chunks(
                collection_name=self.settings.qdrant_collection_name,
                chunks=chunks,
                embeddings=embeddings,
            )
            self.bm25_index.index_chunks(chunks)

        self.indexed_doc_count = len(docs)
        self.indexed_chunk_count = len(chunks)

        logger.info(
            "Initialized corpus index in memory",
            extra_data={"docs": len(docs), "chunks": len(chunks)},
        )
        return len(docs), len(chunks)


_global_container: AppContainer | None = None


def get_container() -> AppContainer:
    """Gets or initializes the global application dependency container."""
    global _global_container
    if _global_container is None:
        _global_container = AppContainer()
    return _global_container


def set_container(container: AppContainer) -> None:
    """Sets the global container (useful for test injection)."""
    global _global_container
    _global_container = container
