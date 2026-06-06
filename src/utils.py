from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def ensure_dir(path: Path) -> Path:
    """Create a directory if it does not exist and return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def setup_logging(log_dir: Path | None = None) -> None:
    """Configure simple console and file logging."""
    log_dir = ensure_dir(log_dir or PROJECT_ROOT / "data" / "logs")
    log_file = log_dir / "app.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
        force=True,
    )


def now_in_timezone(timezone: str) -> datetime:
    """Return current datetime in the configured timezone."""
    return datetime.now(ZoneInfo(timezone))


def today_string(timezone: str) -> str:
    """Return YYYY-MM-DD for the configured timezone."""
    return now_in_timezone(timezone).strftime("%Y-%m-%d")


def read_text(path: Path) -> str:
    """Read a UTF-8 text file."""
    return path.read_text(encoding="utf-8")


def write_json(path: Path, data: object) -> Path:
    """Write JSON with UTF-8 and pretty indentation."""
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def normalize_title(title: str) -> str:
    """Normalize a title for lightweight duplicate detection."""
    lowered = (title or "").strip().lower()
    return re.sub(r"\s+", " ", re.sub(r"[^\w\u4e00-\u9fff]+", " ", lowered)).strip()


def strip_markdown_code_fence(text: str) -> str:
    """Remove surrounding Markdown code fences commonly returned by LLMs."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def truncate_text(text: str, max_chars: int) -> str:
    """Truncate text without raising on empty input."""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."
