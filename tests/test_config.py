"""Unit tests for configuration settings."""

from svearag.core.config import Settings, get_settings


def test_settings_defaults():
    settings = get_settings()
    assert settings.project_name == "SveaRAG Assistant"
    assert settings.embedding_dimension == 384
    assert settings.use_in_memory_vector_store is True
    assert settings.default_top_k == 4
    assert settings.raw_data_dir.exists()


def test_settings_custom():
    custom = Settings(project_name="CustomRAG", embedding_dimension=512)
    assert custom.project_name == "CustomRAG"
    assert custom.embedding_dimension == 512
