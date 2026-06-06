from __future__ import annotations

import logging
from pathlib import Path

from .tavily_client import TavilySearchClient
from .utils import PROJECT_ROOT, today_string, write_json

logger = logging.getLogger(__name__)


class NewsCollector:
    """Collect daily news from configured query groups."""

    def __init__(
        self,
        config: dict,
        tavily_client: TavilySearchClient,
        timezone: str,
        raw_dir: Path | None = None,
    ) -> None:
        self.config = config
        self.tavily_client = tavily_client
        self.timezone = timezone
        self.raw_dir = raw_dir or PROJECT_ROOT / "data" / "raw"

    def collect_daily_news(self) -> list[dict]:
        """Search all configured categories and save raw JSON."""
        search_config = self.config.get("search", {})
        max_results = int(search_config.get("max_results_per_query", 5))
        queries = self.config.get("queries", {})

        all_items: list[dict] = []
        for category, category_queries in queries.items():
            for query in category_queries or []:
                logger.info("Searching category=%s query=%s", category, query)
                items = self.tavily_client.search(
                    query=query,
                    max_results=max_results,
                    category=category,
                )
                all_items.extend(items)

        output = self.raw_dir / f"{today_string(self.timezone)}.json"
        write_json(output, all_items)
        logger.info("Saved %d raw items to %s", len(all_items), output)
        return all_items
