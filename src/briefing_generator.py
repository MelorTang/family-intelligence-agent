from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - exercised only before dependencies are installed
    OpenAI = None  # type: ignore[assignment]

from .utils import PROJECT_ROOT, read_text, strip_markdown_code_fence, today_string

logger = logging.getLogger(__name__)


class BriefingGenerator:
    """Generate a structured Chinese family briefing with an OpenAI-compatible LLM."""

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str,
        config: dict[str, Any],
        timezone: str,
        prompts_dir: Path | None = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.config = config
        self.timezone = timezone
        self.prompts_dir = prompts_dir or PROJECT_ROOT / "prompts"
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=60) if api_key and OpenAI else None

    def generate_daily_briefing(self, items: list[dict]) -> dict:
        """Generate a JSON briefing and always return a dict with markdown."""
        date = today_string(self.timezone)
        selected_items = items[: int(self.config.get("briefing", {}).get("max_news_items", 12))]

        if not self.client:
            logger.warning("LLM_API_KEY is not configured; use fallback briefing.")
            briefing = self._fallback_briefing(date, selected_items, "LLM_API_KEY 未配置，无法生成 LLM 简报。")
            briefing["markdown"] = self.to_markdown(briefing, selected_items)
            return briefing

        system_prompt = read_text(self.prompts_dir / "system_prompt.md")
        daily_prompt = read_text(self.prompts_dir / "daily_briefing_prompt.md")
        user_payload = {
            "date": date,
            "config": self.config.get("briefing", {}),
            "search_results": self._compact_items(selected_items),
        }

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": daily_prompt + "\n\n搜索结果 JSON：\n" + json.dumps(user_payload, ensure_ascii=False),
                    },
                ],
            )
            content = response.choices[0].message.content or ""
        except Exception as exc:
            logger.exception("LLM briefing generation failed: %s", exc)
            briefing = self._fallback_briefing(date, selected_items, f"LLM 调用失败：{exc}")
            briefing["markdown"] = self.to_markdown(briefing, selected_items)
            return briefing

        briefing = self._parse_or_fallback(content, date, selected_items)
        briefing["date"] = date
        briefing.setdefault("title", "今日家庭全球简报")
        briefing["markdown"] = self.to_markdown(briefing, selected_items)
        return briefing

    def to_markdown(self, briefing: dict, raw_items: list[dict] | None = None) -> str:
        """Convert the structured briefing into an Obsidian-friendly Markdown report."""
        date = briefing.get("date") or today_string(self.timezone)
        top_items = briefing.get("top_items") or []
        market = briefing.get("market_temperature") or {}
        observations = briefing.get("investment_observation") or []
        family_action = briefing.get("family_action") or {}
        raw_items = raw_items or []

        lines: list[str] = [
            "---",
            f"date: {date}",
            "type: daily_briefing",
            "source: tavily",
            "audience: family",
            "---",
            "",
            f"# 🌍 {briefing.get('title', '今日家庭全球简报')}",
            "",
            "## 一句话总结",
            briefing.get("one_sentence_summary", "今天暂无足够信息形成明确总结。"),
            "",
            "## 今日最重要的 5 件事",
        ]

        for idx, item in enumerate(top_items[:5], start=1):
            lines.extend(
                [
                    "",
                    f"### {idx}. {item.get('title', '未命名事件')}",
                    f"发生了什么：{item.get('what_happened', '不确定')}",
                    "",
                    f"为什么重要：{item.get('why_it_matters', '不确定')}",
                    "",
                    f"对普通家庭的影响：{item.get('family_impact', '不确定')}",
                    "",
                    f"投资影响：{item.get('investment_impact', '不确定')}",
                    "",
                    f"不确定性：{item.get('uncertainty', '不确定')}",
                    "",
                    "来源：",
                ]
            )
            for source in item.get("sources", []) or []:
                title = source.get("title") or source.get("url") or "来源"
                url = source.get("url", "")
                lines.append(f"- [{title}]({url})" if url else f"- {title}")

        lines.extend(
            [
                "",
                "## 今日投资温度",
                f"- 美股：{market.get('us_stock', '不确定')}",
                f"- A股：{market.get('a_share', '不确定')}",
                f"- 港股：{market.get('hk_stock', '不确定')}",
                f"- 黄金：{market.get('gold', '不确定')}",
                f"- 美元：{market.get('usd', '不确定')}",
                f"- 原油：{market.get('oil', '不确定')}",
                "",
                "## 投资观察",
            ]
        )

        if observations:
            for observation in observations:
                lines.append(
                    f"- {observation.get('asset', '资产')}：{observation.get('level', '🟡 谨慎观察')}。"
                    f"原因：{observation.get('reason', '不确定')} 风险：{observation.get('risk', '不确定')}"
                )
        else:
            lines.append("- 今天没有足够信息形成明确投资观察，保持分散和谨慎。")

        lines.extend(
            [
                "",
                "## 给家人的提醒",
                family_action.get("summary", "今天没有必须马上行动的大事。不要因为单条新闻冲动投资。"),
            ]
        )
        warnings = family_action.get("warnings") or []
        for warning in warnings:
            lines.append(f"- {warning}")

        lines.extend(["", "## 原始来源"])
        for item in raw_items:
            title = item.get("title") or item.get("url") or "来源"
            url = item.get("url", "")
            category = item.get("category", "unknown")
            lines.append(f"- [{title}]({url}) ({category})" if url else f"- {title} ({category})")

        return "\n".join(lines).strip() + "\n"

    def _compact_items(self, items: list[dict]) -> list[dict]:
        compact: list[dict] = []
        for item in items:
            compact.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": (item.get("content") or "")[:1000],
                    "score": item.get("score", 0),
                    "category": item.get("category", ""),
                    "query": item.get("query", ""),
                }
            )
        return compact

    def _parse_or_fallback(self, content: str, date: str, items: list[dict]) -> dict:
        try:
            return json.loads(strip_markdown_code_fence(content))
        except json.JSONDecodeError:
            logger.warning("Initial JSON parse failed; trying to extract JSON object.")

        match = re.search(r"\{.*\}", content, flags=re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                logger.exception("Extracted JSON repair failed.")

        briefing = self._fallback_briefing(date, items, "LLM 返回内容不是合法 JSON，已作为原始 Markdown 保存。")
        briefing["markdown"] = content.strip() or self.to_markdown(briefing, items)
        return briefing

    def _fallback_briefing(self, date: str, items: list[dict], reason: str) -> dict:
        top_items = []
        for item in items[:5]:
            top_items.append(
                {
                    "title": item.get("title", "未命名事件"),
                    "what_happened": item.get("content", "信息不足")[:300],
                    "why_it_matters": "需要进一步确认其影响范围。",
                    "family_impact": "建议仅作为信息观察，不必因为单条消息立即行动。",
                    "investment_impact": "不构成投资建议，相关资产走势仍不确定。",
                    "uncertainty": reason,
                    "sources": [{"title": item.get("title", "来源"), "url": item.get("url", "")}],
                }
            )

        return {
            "date": date,
            "title": "今日家庭全球简报",
            "one_sentence_summary": "今天的信息已完成收集，但自动总结生成不完整，请查看原始来源。",
            "top_items": top_items,
            "market_temperature": {
                "us_stock": "不确定",
                "a_share": "不确定",
                "hk_stock": "不确定",
                "gold": "不确定",
                "usd": "不确定",
                "oil": "不确定",
            },
            "investment_observation": [
                {
                    "asset": "整体市场",
                    "level": "🟡 谨慎观察",
                    "reason": "自动简报生成失败或信息不足。",
                    "risk": "不要基于不完整信息做集中交易。",
                }
            ],
            "family_action": {
                "need_action_today": False,
                "summary": "今天没有必须马上行动的大事。请优先核验来源，避免被单条消息带动情绪。",
                "warnings": [reason],
            },
        }
