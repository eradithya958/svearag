"""Unit tests for embedding providers."""

from unittest.mock import MagicMock, patch

import numpy as np

from svearag.retrieval.embeddings import MockEmbeddingProvider, SentenceTransformerEmbeddingProvider


def test_mock_embedding_provider_dimension_and_determinism():
    provider = MockEmbeddingProvider(dimension=128)
    assert provider.dimension == 128

    vec1 = provider.embed_text("Residence permit in Sweden")
    vec2 = provider.embed_text("Residence permit in Sweden")
    vec3 = provider.embed_text("Completely different topic")

    assert len(vec1) == 128
    assert vec1 == vec2
    assert vec1 != vec3

    # Check unit norm
    norm = np.linalg.norm(vec1)
    assert np.isclose(norm, 1.0, atol=1e-4)


def test_mock_embedding_provider_batch():
    provider = MockEmbeddingProvider(dimension=64)
    texts = ["Text 1", "Text 2", "Text 3"]
    vectors = provider.embed_batch(texts)

    assert len(vectors) == 3
    assert len(vectors[0]) == 64


def test_sentence_transformer_provider_mocked():
    with patch("svearag.retrieval.embeddings.SentenceTransformer") as mock_st_cls:
        mock_instance = MagicMock()
        mock_instance.encode.return_value = np.array(
            [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]], dtype=np.float32
        )
        mock_st_cls.return_value = mock_instance

        provider = SentenceTransformerEmbeddingProvider(dimension=3)
        assert provider.dimension == 3

        batch_vecs = provider.embed_batch(["Hello", "World"])
        assert len(batch_vecs) == 2
        assert len(batch_vecs[0]) == 3

        mock_instance.encode.return_value = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        single_vec = provider.embed_text("Single text")
        assert len(single_vec) == 3


def test_sentence_transformer_empty_batch():
    provider = SentenceTransformerEmbeddingProvider()
    assert provider.embed_batch([]) == []
