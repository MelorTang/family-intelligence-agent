from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only before dependencies are installed
    yaml = None  # type: ignore[assignment]

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - exercised only before dependencies are installed
    def load_dotenv(*_args: object, **_kwargs: object) -> bool:
        return False

from .utils import PROJECT_ROOT


DEFAULT_CONFIG: dict[str, Any] = {
    "app": {"name": "家庭全球资讯与投资观察助手", "language": "zh-CN", "timezone": "Asia/Seoul"},
    "search": {"max_results_per_query": 5, "search_depth": "basic", "include_answer": True, "include_raw_content": False},
    "briefing": {"max_news_items": 12, "final_top_items": 5},
    "queries": {},
}


@dataclass
class Settings:
    """Runtime settings loaded from .env and config.yaml."""

    config: dict[str, Any]
    tavily_api_key: str
    openai_api_key: str
    openai_model: str
    feishu_webhook_url: str
    feishu_secret: str
    obsidian_vault_path: Path
    timezone: str
    project_root: Path = PROJECT_ROOT


def load_settings(config_path: Path | None = None) -> Settings:
    """Load YAML configuration and environment variables."""
    load_dotenv(PROJECT_ROOT / ".env")
    config_path = config_path or PROJECT_ROOT / "config.yaml"

    if yaml and config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
    else:
        config = DEFAULT_CONFIG

    timezone = os.getenv("TIMEZONE") or config.get("app", {}).get("timezone", "Asia/Seoul")
    obsidian_path_raw = os.getenv("OBSIDIAN_VAULT_PATH", "./obsidian_output")
    obsidian_vault_path = Path(obsidian_path_raw)
    if not obsidian_vault_path.is_absolute():
        obsidian_vault_path = PROJECT_ROOT / obsidian_vault_path

    return Settings(
        config=config,
        tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        feishu_webhook_url=os.getenv("FEISHU_WEBHOOK_URL", ""),
        feishu_secret=os.getenv("FEISHU_SECRET", ""),
        obsidian_vault_path=obsidian_vault_path,
        timezone=timezone,
    )
