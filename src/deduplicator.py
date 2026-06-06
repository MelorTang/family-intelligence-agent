from __future__ import annotations

import hashlib

from .utils import normalize_title


class Deduplicator:
    """Simple duplicate remover based on URL, normalized title and content hash."""

    def deduplicate(self, items: list[dict]) -> list[dict]:
        """Deduplicate items while keeping the higher-quality version."""
        selected: dict[str, dict] = {}

        for item in items:
            keys = self._keys_for_item(item)
            existing_key = next((key for key in keys if key in selected), None)

            if existing_key is None:
                primary_key = keys[0] if keys else f"item:{len(selected)}"
                selected[primary_key] = item
                continue

            existing = selected[existing_key]
            winner = self._better_item(existing, item)
            if winner is item:
                for key in keys:
                    selected[key] = item

        unique_by_url_or_title: dict[str, dict] = {}
        for item in selected.values():
            stable_key = item.get("url") or normalize_title(item.get("title", ""))
            unique_by_url_or_title[stable_key] = self._better_item(
                unique_by_url_or_title.get(stable_key, {}),
                item,
            )
        return sorted(unique_by_url_or_title.values(), key=lambda x: x.get("score", 0), reverse=True)

    def _keys_for_item(self, item: dict) -> list[str]:
        keys: list[str] = []
        if item.get("url"):
            keys.append(f"url:{item['url'].strip()}")
        title_key = normalize_title(item.get("title", ""))
        if title_key:
            keys.append(f"title:{title_key}")
        content = (item.get("content") or "")[:200]
        if content:
            digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
            keys.append(f"content:{digest}")
        return keys

    def _better_item(self, left: dict, right: dict) -> dict:
        left_score = float(left.get("score") or 0)
        right_score = float(right.get("score") or 0)
        if right_score > left_score:
            return right
        if right_score == left_score and len(right.get("content", "")) > len(left.get("content", "")):
            return right
        return left
