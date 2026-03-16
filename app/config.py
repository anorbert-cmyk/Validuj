from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_base_url: str
    app_env: str
    database_path: str
    openrouter_api_key: str | None
    openrouter_base_url: str
    openrouter_research_model: str
    openrouter_reasoning_model: str
    openrouter_design_model: str
    tavily_api_key: str | None
    local_model_id: str

    @property
    def has_openrouter(self) -> bool:
        return bool(self.openrouter_api_key)

    @property
    def has_tavily(self) -> bool:
        return bool(self.tavily_api_key)


def _env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        app_name=_env("APP_NAME", "Validuj") or "Validuj",
        app_base_url=_env("APP_BASE_URL", "http://127.0.0.1:8000") or "http://127.0.0.1:8000",
        app_env=_env("APP_ENV", "development") or "development",
        database_path=_env("DATABASE_PATH", "/workspace/data/validuj.sqlite3") or "/workspace/data/validuj.sqlite3",
        openrouter_api_key=_env("OPENROUTER_API_KEY"),
        openrouter_base_url=_env("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        or "https://openrouter.ai/api/v1",
        openrouter_research_model=_env("OPENROUTER_RESEARCH_MODEL", "perplexity/sonar-pro")
        or "perplexity/sonar-pro",
        openrouter_reasoning_model=_env("OPENROUTER_REASONING_MODEL", "anthropic/claude-3.7-sonnet")
        or "anthropic/claude-3.7-sonnet",
        openrouter_design_model=_env("OPENROUTER_DESIGN_MODEL", "openai/gpt-4.1")
        or "openai/gpt-4.1",
        tavily_api_key=_env("TAVILY_API_KEY"),
        local_model_id=_env("LOCAL_MODEL_ID", "local-synthesis-engine") or "local-synthesis-engine",
    )
