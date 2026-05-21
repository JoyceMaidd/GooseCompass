from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Loads and validates all required environment variables.

    All fields are required — missing any will raise ValidationError at startup.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    mongodb_uri: str
    mongodb_db_name: str
    mongodb_collection_chunks: str
    openai_api_key: str
    openrouter_api_key: str
    openrouter_generation_model: str
    openrouter_rewriter_model: str


settings = Settings()
