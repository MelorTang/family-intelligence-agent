from __future__ import annotations

import argparse
import logging
from pathlib import Path

from src.briefing_generator import BriefingGenerator
from src.config import Settings, load_settings
from src.deduplicator import Deduplicator
from src.feishu_publisher import FeishuPublisher
from src.knowledge_base import KnowledgeBaseManager
from src.news_collector import NewsCollector
from src.obsidian_writer import ObsidianWriter
from src.scheduler import LocalScheduler
from src.tavily_client import TavilySearchClient
from src.utils import PROJECT_ROOT, setup_logging, today_string, write_json

logger = logging.getLogger(__name__)


def run_daily(settings: Settings | None = None) -> dict:
    """Run the complete daily collection, generation, write and publish flow."""
    settings = settings or load_settings()
    setup_logging(PROJECT_ROOT / "data" / "logs")
    logger.info("Starting daily run.")

    tavily = TavilySearchClient(
        api_key=settings.tavily_api_key,
        timezone=settings.timezone,
        search_config=settings.config.get("search", {}),
    )
    collector = NewsCollector(settings.config, tavily, settings.timezone)
    raw_items = collector.collect_daily_news()

    deduplicator = Deduplicator()
    deduped_items = deduplicator.deduplicate(raw_items)
    logger.info("Deduplicated %d raw items to %d items.", len(raw_items), len(deduped_items))

    generator = BriefingGenerator(
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        base_url=settings.llm_base_url,
        config=settings.config,
        timezone=settings.timezone,
    )
    briefing = generator.generate_daily_briefing(deduped_items)

    writer = ObsidianWriter(settings.obsidian_vault_path, settings.timezone)
    markdown_path = writer.write_daily(briefing)
    logger.info("Saved briefing markdown to %s", markdown_path)

    processed_path = PROJECT_ROOT / "data" / "processed" / f"{today_string(settings.timezone)}.json"
    write_json(
        processed_path,
        {
            "briefing": briefing,
            "raw_count": len(raw_items),
            "deduplicated_count": len(deduped_items),
            "markdown_path": str(markdown_path),
        },
    )
    logger.info("Saved processed JSON to %s", processed_path)

    publisher = FeishuPublisher(
        webhook_url=settings.feishu_webhook_url,
        secret=settings.feishu_secret,
        timezone=settings.timezone,
    )
    feishu_sent = publisher.send_daily_briefing(briefing)

    result = {
        "date": briefing.get("date"),
        "raw_count": len(raw_items),
        "deduplicated_count": len(deduped_items),
        "markdown_path": str(markdown_path),
        "processed_path": str(processed_path),
        "feishu_sent": feishu_sent,
    }
    logger.info("Daily run finished: %s", result)
    print_run_result(result)
    return result


def run_weekly(settings: Settings | None = None) -> None:
    """Generate a weekly Obsidian knowledge summary from recent daily reports."""
    settings = settings or load_settings()
    setup_logging(PROJECT_ROOT / "data" / "logs")
    manager = KnowledgeBaseManager(
        vault_path=Path(settings.obsidian_vault_path),
        llm_api_key=settings.llm_api_key,
        llm_model=settings.llm_model,
        llm_base_url=settings.llm_base_url,
        timezone=settings.timezone,
    )
    result = manager.generate_weekly_knowledge()
    logger.info("Weekly knowledge run finished: %s", result)

    print("\n周报生成完成")
    print(f"- 周次：{result.get('week')}")
    print(f"- 使用日报数：{len(result.get('daily_files', []))}")
    print(f"- 周报：{result.get('weekly_path')}")
    print(f"- 更新主题页数：{len(result.get('topic_paths', []))}")


def start_scheduler() -> None:
    """Start local scheduled daily runs."""
    settings = load_settings()
    setup_logging(PROJECT_ROOT / "data" / "logs")
    scheduler = LocalScheduler(settings.config, daily_job=lambda: run_daily(settings))
    scheduler.start()


def print_run_result(result: dict) -> None:
    """Print a compact command-line summary."""
    print("\n运行完成")
    print(f"- 日期：{result.get('date')}")
    print(f"- 原始结果数：{result.get('raw_count')}")
    print(f"- 去重后结果数：{result.get('deduplicated_count')}")
    print(f"- Markdown：{result.get('markdown_path')}")
    print(f"- Processed JSON：{result.get('processed_path')}")
    print(f"- 飞书推送：{'成功' if result.get('feishu_sent') else '未发送或失败'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="家庭全球资讯与投资观察助手")
    parser.add_argument("command", choices=["run-daily", "run-weekly", "schedule"])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "run-daily":
        run_daily()
    elif args.command == "run-weekly":
        run_weekly()
    elif args.command == "schedule":
        start_scheduler()


if __name__ == "__main__":
    main()
