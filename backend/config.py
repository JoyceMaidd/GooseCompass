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
    jwt_secret: str
    jwt_expiry_minutes: int
    email_provider: str
    email_api_key: str
    email_from: str
    otp_ttl_minutes: int
    otp_max_attempts: int
    otp_resend_cooldown_seconds: int
    otp_code_length: int


settings = Settings()
