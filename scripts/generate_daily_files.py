#!/usr/bin/env python3
"""Generate idempotent Hermes inbox Markdown files for an Obsidian vault."""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path


def frontmatter(fields: list[tuple[str, object]]) -> str:
    lines = ["---"]
    for key, value in fields:
        if isinstance(value, list):
            lines.append(f"{key}:")
            lines.extend(f"  - {item}" for item in value)
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines)


def write_if_needed(path: Path, content: str, dry_run: bool, overwrite: bool) -> str:
    if path.exists() and not overwrite:
        return f"skip existing: {path}"
    if dry_run:
        action = "overwrite" if path.exists() else "create"
        return f"[dry-run] {action}: {path}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"wrote: {path}"


def build_news(today: str) -> str:
    return f"""{frontmatter([
        ("type", "source"),
        ("source_type", "news_digest"),
        ("source", "hermes"),
        ("status", "inbox"),
        ("review", "pending"),
        ("created_by", "hermes"),
        ("created", today),
        ("tags", ["inbox", "hermes", "news"]),
    ])}

# Daily News - {today}

## Summary

## Important Items

## Potential Follow-up Questions

## Candidate Knowledge Notes

## Raw Items
"""


def build_captures(today: str) -> str:
    return f"""{frontmatter([
        ("type", "capture"),
        ("source", "hermes"),
        ("status", "inbox"),
        ("review", "pending"),
        ("created_by", "hermes"),
        ("created", today),
        ("tags", ["inbox", "hermes", "capture"]),
    ])}

# Daily Captures - {today}

## Captures

## Possible Projects

## Possible Concepts

## Follow-up
"""


def build_briefing(today: str) -> str:
    return f"""{frontmatter([
        ("type", "daily_briefing"),
        ("source", "hermes"),
        ("status", "draft"),
        ("review", "pending"),
        ("created_by", "hermes"),
        ("created", today),
        ("tags", ["briefing", "daily"]),
    ])}

# Daily Briefing - {today}

## Top Highlights

## What Matters

## Recommended Actions

## Items to Review in Obsidian
"""


def build_weekly_review(today: str) -> str:
    year, week, _ = dt.date.fromisoformat(today).isocalendar()
    week_id = f"{year}-W{week:02d}"
    return f"""{frontmatter([
        ("type", "weekly_review"),
        ("source", "hermes"),
        ("status", "draft"),
        ("review", "pending"),
        ("created_by", "hermes"),
        ("created", today),
        ("week", week_id),
        ("tags", ["review", "weekly"]),
    ])}

# Weekly Review - {week_id}

## Weekly Highlights

## Recurring Themes

## Candidate Concepts

## Candidate Projects

## Questions for Local Review
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", required=True, help="Path to the Obsidian vault")
    parser.add_argument("--date", default=dt.date.today().isoformat())
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--no-news", action="store_true")
    parser.add_argument("--no-captures", action="store_true")
    parser.add_argument("--no-briefing", action="store_true")
    parser.add_argument("--weekly-review", action="store_true")
    args = parser.parse_args()

    vault = Path(args.vault).expanduser().resolve()
    outputs: list[tuple[Path, str]] = []
    if not args.no_news:
        outputs.append((vault / "00_Inbox/Hermes/News" / f"{args.date}-news.md", build_news(args.date)))
    if not args.no_captures:
        outputs.append((vault / "00_Inbox/Hermes/Captures" / f"{args.date}-captures.md", build_captures(args.date)))
    if not args.no_briefing:
        outputs.append((vault / "05_Output/Daily_Briefings" / f"{args.date}-briefing.md", build_briefing(args.date)))
    if args.weekly_review:
        year, week, _ = dt.date.fromisoformat(args.date).isocalendar()
        outputs.append((vault / "05_Output/Weekly_Reviews" / f"{year}-W{week:02d}.md", build_weekly_review(args.date)))

    for path, content in outputs:
        print(write_if_needed(path, content, args.dry_run, args.overwrite))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
