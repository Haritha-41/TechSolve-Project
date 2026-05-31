from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    chroma_persist_dir: str = "./chroma_store"
    frontend_origin: str = "http://localhost:3000"
    frontend_origins: str = "http://localhost:3000,http://localhost:3001,http://localhost:3002"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    whisper_model: str = "tiny"
    retrieval_k: int = 6
    instagram_cookies_file: str = ""
    instagram_view_provider: str = ""
    apify_token: str = ""
    apify_reel_actor_id: str = "apidojo/instagram-scraper-api"
    apify_timeout_seconds: int = 180
    app_name: str = "SocialSense RAG"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_frontend_origins() -> list[str]:
    settings = get_settings()
    origins = settings.frontend_origins or settings.frontend_origin
    return [origin.strip() for origin in origins.split(",") if origin.strip()]
