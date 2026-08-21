from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Loads and validates all required environment variables.

    All fields are required — missing any will raise ValidationError at startup.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    mongodb_uri: str
    mongodb_db_name: str
    mongodb_collection_chunks: str
    openai_api_key: str
    openrouter_api_key: str
    openrouter_generation_model: str
    openrouter_rewriter_model: str
    openrouter_eval_judge_model: str
    frontend_origin: str
    postgres_uri: str
    monthly_spend_cap_usd: float
    user_monthly_quota_tokens: int
    logfire_api_key: str = ""
    logfire_enabled: bool = True


settings = Settings()
