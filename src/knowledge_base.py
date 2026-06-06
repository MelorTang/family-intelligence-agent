from __future__ import annotations

import logging
from datetime import timedelta
from pathlib import Path
from typing import Any

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - exercised only before dependencies are installed
    OpenAI = None  # type: ignore[assignment]

from .utils import PROJECT_ROOT, ensure_dir, now_in_timezone, read_text, truncate_text

logger = logging.getLogger(__name__)


DEFAULT_TOPICS = {
    "AI": ["AI", "人工智能", "大模型", "芯片", "算力", "OpenAI", "NVIDIA", "英伟达"],
    "黄金": ["黄金", "gold", "避险"],
    "美股": ["美股", "US stock", "Fed", "Treasury", "Nasdaq", "标普", "纳斯达克"],
    "A股": ["A股", "中国股市", "沪深", "创业板"],
    "港股": ["港股", "恒生", "科技股"],
    "中国经济": ["中国经济", "房地产", "就业", "消费", "政策"],
    "地缘风险": ["地缘", "战争", "冲突", "制裁", "原油", "oil"],
    "家庭防诈骗": ["诈骗", "fraud", "scam", "养老", "食品安全", "医疗"],
}


class KnowledgeBaseManager:
    """Create weekly summaries and lightweight topic notes for Obsidian."""

    def __init__(
        self,
        vault_path: Path,
        llm_api_key: str,
        llm_model: str,
        llm_base_url: str,
        timezone: str,
        prompts_dir: Path | None = None,
    ) -> None:
        self.vault_path = vault_path
        self.llm_model = llm_model
        self.llm_base_url = llm_base_url
        self.timezone = timezone
        self.prompts_dir = prompts_dir or PROJECT_ROOT / "prompts"
        self.client = OpenAI(api_key=llm_api_key, base_url=llm_base_url, timeout=60) if llm_api_key and OpenAI else None

    def generate_weekly_knowledge(self) -> dict[str, Any]:
        """Generate a weekly report from recent daily Markdown files and update topic notes."""
        daily_files = self._recent_daily_files(days=7)
        week_id = now_in_timezone(self.timezone).strftime("%G-W%V")
        weekly_markdown = self._build_weekly_markdown(week_id, daily_files)
        weekly_path = self._write_weekly(week_id, weekly_markdown)
        topic_paths = self._update_topic_notes(week_id, weekly_markdown, daily_files)
        return {
            "week": week_id,
            "daily_files": [str(path) for path in daily_files],
            "weekly_path": str(weekly_path),
            "topic_paths": [str(path) for path in topic_paths],
        }

    def _recent_daily_files(self, days: int) -> list[Path]:
        daily_dir = self.vault_path / "01_Daily"
        if not daily_dir.exists():
            return []

        today = now_in_timezone(self.timezone).date()
        names = {(today - timedelta(days=offset)).strftime("%Y-%m-%d.md") for offset in range(days)}
        files = [path for path in daily_dir.glob("*.md") if path.name in names]
        return sorted(files)

    def _build_weekly_markdown(self, week_id: str, daily_files: list[Path]) -> str:
        if not daily_files:
            return self._fallback_weekly_markdown(week_id, [], "最近 7 天没有找到日报文件。")

        source_text = "\n\n".join(
            f"## 来源文件：{path.name}\n\n{truncate_text(path.read_text(encoding='utf-8'), 6000)}"
            for path in daily_files
        )

        if not self.client:
            return self._fallback_weekly_markdown(week_id, daily_files, "LLM_API_KEY 未配置，使用规则 fallback。")

        prompt = read_text(self.prompts_dir / "weekly_knowledge_prompt.md")
        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                temperature=0.2,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个谨慎、温和、适合家庭使用的中文知识库整理助手。",
                    },
                    {
                        "role": "user",
                        "content": f"{prompt}\n\n周次：{week_id}\n\n日报材料：\n{source_text}",
                    },
                ],
            )
            content = (response.choices[0].message.content or "").strip()
            if content:
                return self._with_weekly_frontmatter(week_id, content)
        except Exception as exc:
            logger.exception("Weekly knowledge generation failed: %s", exc)
            return self._fallback_weekly_markdown(week_id, daily_files, f"LLM 周报生成失败：{exc}")

        return self._fallback_weekly_markdown(week_id, daily_files, "LLM 周报返回为空。")

    def _write_weekly(self, week_id: str, markdown: str) -> Path:
        weekly_dir = ensure_dir(self.vault_path / "02_Weekly")
        path = weekly_dir / f"{week_id}.md"
        path.write_text(markdown, encoding="utf-8")
        return path

    def _update_topic_notes(self, week_id: str, weekly_markdown: str, daily_files: list[Path]) -> list[Path]:
        if not daily_files:
            return []

        topics_dir = ensure_dir(self.vault_path / "03_Topics")
        source_text = weekly_markdown + "\n\n" + "\n".join(path.name for path in daily_files)
        updated: list[Path] = []

        for topic, keywords in DEFAULT_TOPICS.items():
            if not any(keyword.lower() in source_text.lower() for keyword in keywords):
                continue

            path = topics_dir / f"{topic}.md"
            existing = path.read_text(encoding="utf-8") if path.exists() else self._topic_header(topic)
            entry = self._topic_entry(week_id, topic, daily_files)
            if entry.strip() not in existing:
                path.write_text(existing.rstrip() + "\n\n" + entry, encoding="utf-8")
            updated.append(path)

        return updated

    def _topic_header(self, topic: str) -> str:
        return "\n".join(
            [
                "---",
                f"topic: {topic}",
                "type: topic_note",
                "source: weekly_briefing",
                "---",
                "",
                f"# {topic}",
                "",
                "用于沉淀家庭资讯日报和周报中反复出现的重要主题。",
            ]
        )

    def _topic_entry(self, week_id: str, topic: str, daily_files: list[Path]) -> str:
        daily_links = "、".join(f"[[01_Daily/{path.stem}|{path.stem}]]" for path in daily_files)
        return "\n".join(
            [
                f"## {week_id}",
                "",
                f"- 主题：{topic}",
                f"- 周报：[[02_Weekly/{week_id}|{week_id}]]",
                f"- 相关日报：{daily_links or '暂无'}",
                "- 备注：由周报自动索引。后续可由 Hermes 根据需要补充人工理解和长期判断。",
            ]
        )

    def _fallback_weekly_markdown(self, week_id: str, daily_files: list[Path], reason: str) -> str:
        lines = [
            "---",
            f"week: {week_id}",
            "type: weekly_briefing",
            "source: daily_markdown",
            "audience: family",
            "---",
            "",
            "# 本周家庭全球观察周报",
            "",
            "## 一句话总结",
            f"周报自动生成不完整：{reason}",
            "",
            "## 本周日报索引",
        ]
        if daily_files:
            for path in daily_files:
                lines.append(f"- [[01_Daily/{path.stem}|{path.stem}]]")
        else:
            lines.append("- 暂无日报文件。")

        lines.extend(
            [
                "",
                "## 投资观察与风险提示",
                "本周材料不足或自动生成失败。不要基于不完整信息做集中交易。",
                "",
                "## 下周观察清单",
                "- 继续观察全球重大新闻、主要市场温度、地缘风险和家庭生活风险。",
            ]
        )
        return "\n".join(lines).strip() + "\n"

    def _with_weekly_frontmatter(self, week_id: str, markdown: str) -> str:
        if markdown.lstrip().startswith("---"):
            return markdown.strip() + "\n"
        return "\n".join(
            [
                "---",
                f"week: {week_id}",
                "type: weekly_briefing",
                "source: daily_markdown",
                "audience: family",
                "---",
                "",
                markdown.strip(),
                "",
            ]
        )
