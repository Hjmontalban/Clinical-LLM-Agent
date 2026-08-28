import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parents[2]
_ENV_FILE = _BACKEND_DIR / ".env"


def _default_database_url() -> str:
    # Vercel serverless filesystem is read-only except /tmp
    if os.getenv("VERCEL"):
        return "sqlite+aiosqlite:////tmp/cea.db"
    return "sqlite+aiosqlite:///./cea.db"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Clinical Evidence Assistant"
    debug: bool = False
    database_url: str = _default_database_url()
    cors_origins: str = (
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:3001,http://localhost:3002,http://localhost:3003"
    )

    llm_provider: str = "groq"
    groq_api_key: str = ""
    gemini_api_key: str = ""
    openai_api_key: str = ""

    groq_model: str = "llama-3.3-70b-versatile"
    gemini_model: str = "gemini-2.0-flash"

    semantic_scholar_api_key: str = ""
    ncbi_email: str = "cea@example.com"
    ncbi_tool_name: str = "ClinicalEvidenceAssistant"
    ncbi_api_key: str = ""
    crossref_mailto: str = "cea@example.com"

    jwt_secret: str = "change-me-in-production"
    rate_limit_per_minute: int = 30

    max_papers_per_search: int = 25
    max_papers_for_synthesis: int = 12

    @property
    def is_vercel(self) -> bool:
        return os.getenv("VERCEL") == "1"

    @property
    def cors_origin_list(self) -> list[str]:
        origins = [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        vercel_url = os.getenv("VERCEL_URL")
        if vercel_url:
            origins.append(f"https://{vercel_url}")
        return origins


@lru_cache
def get_settings() -> Settings:
    return Settings()
