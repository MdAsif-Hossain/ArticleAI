from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # The URL of your n8n Cloud webhook
    n8n_webhook_url: str = "https://your-workspace.app.n8n.cloud/webhook/process-article"

    # The Localtunnel URL (so n8n Cloud can talk back to this backend)
    backend_callback_url: str = "https://your-localtunnel-url.loca.lt/api/callback"

    # CORS
    cors_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
