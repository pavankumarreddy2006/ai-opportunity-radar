from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="development", alias="APP_ENV")
    database_url: str = Field(default="sqlite:///./ai_news_collector.db", alias="DATABASE_URL")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openrouter_api_key: str | None = Field(default=None, alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", alias="OPENROUTER_BASE_URL")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")
    secret_key: str = Field(default="change-me-render-secret", alias="SECRET_KEY")
    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")
    frontend_url: str = Field(default="http://localhost:3000", alias="FRONTEND_URL")
    reddit_user_agent: str = Field(default="ai-news-collector/1.0", alias="REDDIT_USER_AGENT")
    youtube_feed_urls: str = Field(default="", alias="YOUTUBE_FEED_URLS")
    update_news_token: str | None = Field(default=None, alias="UPDATE_NEWS_TOKEN")

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        if self.database_url.startswith("postgres://"):
            return self.database_url.replace("postgres://", "postgresql+psycopg://", 1)
        return self.database_url

    @property
    def cors_origin_list(self) -> list[str]:
        origins: list[str] = []
        for item in self.cors_origins.split(","):
            origin = item.strip()
            if not origin:
                continue
            if origin != "*" and not origin.startswith(("http://", "https://")):
                origin = f"https://{origin}"
            origins.append(origin)
        return origins

    @property
    def youtube_feed_list(self) -> list[str]:
        return [item.strip() for item in self.youtube_feed_urls.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
