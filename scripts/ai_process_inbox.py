#!/usr/bin/env python3
"""Mockable AI post-processing for Hermes inbox files.

The MVP intentionally ships with a deterministic mock implementation. Wire a
provider behind build_ai_review when an API key is available in the environment.
"""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path


def build_ai_review(today: str, source_paths: list[Path]) -> str:
    sources = "\n".join(f"- [[{path.stem}]]" for path in source_paths) or "- No source files found."
    return f"""---
type: ai_processed
source: hermes
status: draft
review: pending
created_by: ai
confidence: low
created: {today}
tags:
  - ai-processed
  - to-review
---

# AI Review - {today}

## Suggested Concepts

## Suggested Projects

## Suggested Questions

## Suggested Links

{sources}

## Possible Long-term Notes

## Warnings

- The content below is AI-generated and must be reviewed manually.
- This MVP used mock processing because no provider is configured.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", required=True)
    parser.add_argument("--date", default=dt.date.today().isoformat())
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    vault = Path(args.vault).expanduser().resolve()
    source_paths = [
        vault / "00_Inbox/Hermes/News" / f"{args.date}-news.md",
        vault / "00_Inbox/Hermes/Captures" / f"{args.date}-captures.md",
    ]
    existing_sources = [path for path in source_paths if path.exists()]
    output_path = vault / "00_Inbox/AI_Processed/To_Review" / f"{args.date}-ai-review.md"

    if output_path.exists() and not args.overwrite:
        print(f"skip existing: {output_path}")
        return 0

    if args.dry_run:
        action = "overwrite" if output_path.exists() else "create"
        print(f"[dry-run] {action}: {output_path}")
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_ai_review(args.date, existing_sources), encoding="utf-8")
    print(f"wrote: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
