from __future__ import annotations

from pathlib import Path

from .utils import ensure_dir, today_string


class ObsidianWriter:
    """Write generated briefings into an Obsidian vault."""

    def __init__(self, vault_path: Path, timezone: str) -> None:
        self.vault_path = vault_path
        self.timezone = timezone

    def write_daily(self, briefing: dict) -> Path:
        """Write daily Markdown to {vault}/01_Daily/YYYY-MM-DD.md."""
        daily_dir = ensure_dir(self.vault_path / "01_Daily")
        date = briefing.get("date") or today_string(self.timezone)
        path = daily_dir / f"{date}.md"
        path.write_text(briefing.get("markdown", ""), encoding="utf-8")
        return path
