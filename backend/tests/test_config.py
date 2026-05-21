import pytest
from pydantic import ValidationError

from backend.config import Settings, settings


def test_settings_loaded():
    """All required fields are non-empty when .env is present."""
    assert settings.mongodb_uri
    assert settings.mongodb_db_name
    assert settings.mongodb_collection_chunks
    assert settings.openai_api_key
    assert settings.openrouter_api_key
    assert settings.openrouter_generation_model
    assert settings.openrouter_rewriter_model


def test_validation_error_on_missing_field(monkeypatch, tmp_path):
    """ValidationError is raised when a required field is absent."""
    env_file = tmp_path / ".env"
    env_file.write_text("MONGODB_DB_NAME=test\n")

    required_keys = [
        "MONGODB_URI",
        "MONGODB_DB_NAME",
        "MONGODB_COLLECTION_CHUNKS",
        "OPENAI_API_KEY",
        "OPENROUTER_API_KEY",
        "OPENROUTER_GENERATION_MODEL",
        "OPENROUTER_REWRITER_MODEL",
    ]
    for key in required_keys:
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=str(env_file))
