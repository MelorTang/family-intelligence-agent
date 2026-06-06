from __future__ import annotations

import logging
from typing import Any

try:
    from tavily import TavilyClient
except ImportError:  # pragma: no cover - exercised only before dependencies are installed
    TavilyClient = None  # type: ignore[assignment]

from .utils import now_in_timezone

logger = logging.getLogger(__name__)


class TavilySearchClient:
    """Thin wrapper around Tavily search with safe per-query failures."""

    def __init__(
        self,
        api_key: str,
        timezone: str,
        search_config: dict[str, Any] | None = None,
    ) -> None:
        self.api_key = api_key
        self.timezone = timezone
        self.search_config = search_config or {}
        self.client = TavilyClient(api_key=api_key) if api_key and TavilyClient else None

    def search(self, query: str, max_results: int = 5, category: str = "") -> list[dict]:
        """Search Tavily and return normalized result dictionaries."""
        if not self.client:
            logger.warning("TAVILY_API_KEY is not configured; skip query: %s", query)
            return []

        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth=self.search_config.get("search_depth", "basic"),
                include_answer=self.search_config.get("include_answer", True),
                include_raw_content=self.search_config.get("include_raw_content", False),
            )
        except Exception as exc:
            logger.exception("Tavily query failed: %s (%s)", query, exc)
            return []

        fetched_at = now_in_timezone(self.timezone).isoformat()
        results = response.get("results", []) if isinstance(response, dict) else []
        normalized: list[dict] = []
        for item in results:
            normalized.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content") or item.get("raw_content") or "",
                    "score": item.get("score", 0),
                    "query": query,
                    "category": category,
                    "fetched_at": fetched_at,
                }
            )
        return normalized
