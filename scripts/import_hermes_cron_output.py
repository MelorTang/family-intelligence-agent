#!/usr/bin/env python3
"""Import Hermes cron response Markdown into the Obsidian vault.

This is a deterministic fallback for Hermes cron runs that deliver a Feishu
summary but do not execute file writes from the skill prompt.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
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


def is_empty_placeholder(path: Path) -> bool:
    if not path.exists():
        return True
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return True
    body = re.sub(r"(?s)^---\n.*?\n---\n?", "", text).strip()
    body_lines = [line.strip() for line in body.splitlines() if line.strip()]
    meaningful = [
        line
        for line in body_lines
        if not line.startswith("#")
        and line
        not in {
            "## Summary",
            "## Important Items",
            "## Potential Follow-up Questions",
            "## Candidate Knowledge Notes",
            "## Raw Items",
            "## Captures",
            "## Possible Projects",
            "## Possible Concepts",
            "## Follow-up",
            "## Top Highlights",
            "## What Matters",
            "## Recommended Actions",
            "## Items to Review in Obsidian",
        }
    ]
    return not meaningful


def extract_response(text: str) -> str | None:
    marker = "## Response"
    if marker not in text:
        return None
    response = text.split(marker, 1)[1].strip()
    response = re.split(r"\n##\s+", response, maxsplit=1)[0].strip()
    return response or None


def find_cron_output(output_dir: Path, date: str, job_id: str | None) -> Path | None:
    roots = [output_dir / job_id] if job_id else sorted(p for p in output_dir.iterdir() if p.is_dir())
    candidates: list[Path] = []
    for root in roots:
        if root.exists():
            candidates.extend(root.glob(f"{date}_*.md"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def build_briefing(date: str, response: str, source_file: Path) -> str:
    return f"""{frontmatter([
        ("type", "daily_briefing"),
        ("source", "hermes"),
        ("status", "draft"),
        ("review", "pending"),
        ("created_by", "hermes"),
        ("created", date),
        ("recovered_from", str(source_file)),
        ("tags", ["briefing", "daily", "recovered"]),
    ])}

# Daily Briefing - {date}

{response}
"""


def build_news(date: str, response: str, source_file: Path) -> str:
    return f"""{frontmatter([
        ("type", "source"),
        ("source_type", "news_digest"),
        ("source", "hermes"),
        ("status", "inbox"),
        ("review", "pending"),
        ("created_by", "hermes"),
        ("created", date),
        ("recovered_from", str(source_file)),
        ("tags", ["inbox", "hermes", "news", "recovered"]),
    ])}

# Daily News - {date}

## Summary

This file was recovered from Hermes cron output because the cron response did not write a structured News Digest.

## Important Items

See the recovered briefing below. Claims require review before promotion into long-term knowledge.

## Potential Follow-up Questions

- Which claims need direct source URLs?
- Which items deserve Source, Concept, or Insight notes?

## Candidate Knowledge Notes

## Raw Items

```markdown
{response}
```
"""


def build_captures(date: str, response: str, source_file: Path) -> str:
    return f"""{frontmatter([
        ("type", "capture"),
        ("source", "hermes"),
        ("status", "inbox"),
        ("review", "pending"),
        ("created_by", "hermes"),
        ("created", date),
        ("recovered_from", str(source_file)),
        ("tags", ["inbox", "hermes", "capture", "recovered"]),
    ])}

# Daily Captures - {date}

## Captures

Recovered from Hermes cron output. The original run did not provide separate structured captures.

## Possible Projects

## Possible Concepts

## Follow-up

- Review the briefing and create durable notes only after source checking.
"""


def write_recovered(path: Path, content: str, dry_run: bool) -> str:
    if path.exists() and not is_empty_placeholder(path):
        return f"skip substantive existing: {path}"
    if dry_run:
        action = "overwrite placeholder" if path.exists() else "create"
        return f"[dry-run] {action}: {path}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"wrote recovered: {path}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", required=True, help="Path to the Obsidian vault")
    parser.add_argument("--date", default=dt.date.today().isoformat())
    parser.add_argument("--output-dir", default="~/.hermes/cron/output")
    parser.add_argument("--job-id", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    vault = Path(args.vault).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    if not output_dir.exists():
        print(f"skip cron import: output dir not found: {output_dir}")
        return 0

    source_file = find_cron_output(output_dir, args.date, args.job_id)
    if source_file is None:
        print(f"skip cron import: no Hermes cron output for {args.date}")
        return 0

    response = extract_response(source_file.read_text(encoding="utf-8"))
    if not response:
        print(f"skip cron import: no ## Response content in {source_file}")
        return 0

    outputs = [
        (
            vault / "00_Inbox/Hermes/News" / f"{args.date}-news.md",
            build_news(args.date, response, source_file),
        ),
        (
            vault / "00_Inbox/Hermes/Captures" / f"{args.date}-captures.md",
            build_captures(args.date, response, source_file),
        ),
        (
            vault / "05_Output/Daily_Briefings" / f"{args.date}-briefing.md",
            build_briefing(args.date, response, source_file),
        ),
    ]

    for path, content in outputs:
        print(write_recovered(path, content, args.dry_run))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
