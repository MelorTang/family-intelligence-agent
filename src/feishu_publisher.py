from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import time

try:
    import requests
except ImportError:  # pragma: no cover - exercised only before dependencies are installed
    requests = None  # type: ignore[assignment]

from .utils import today_string, truncate_text

logger = logging.getLogger(__name__)


class FeishuPublisher:
    """Publish text messages to a Feishu custom bot webhook."""

    def __init__(self, webhook_url: str, secret: str = "", timeout: int = 15, timezone: str = "Asia/Seoul") -> None:
        self.webhook_url = webhook_url
        self.secret = secret
        self.timeout = timeout
        self.timezone = timezone

    def send_text(self, text: str) -> bool:
        """Send a plain text Feishu bot message."""
        if not self.webhook_url:
            logger.warning("FEISHU_WEBHOOK_URL is not configured; skip publishing.")
            return False
        if requests is None:
            logger.warning("requests is not installed; skip Feishu publishing.")
            return False

        payload = {
            "msg_type": "text",
            "content": {"text": truncate_text(text, 3000)},
        }
        if self.secret:
            timestamp = str(int(time.time()))
            payload["timestamp"] = timestamp
            payload["sign"] = self._sign(timestamp)

        try:
            response = requests.post(self.webhook_url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            logger.exception("Feishu publish failed: %s", exc)
            return False

        ok = data.get("code") in (0, None) or data.get("StatusCode") in (0, None)
        if not ok:
            logger.error("Feishu returned non-success response: %s", data)
        return ok

    def send_daily_briefing(self, briefing: dict) -> bool:
        """Build and send a concise daily briefing text."""
        return self.send_text(self._build_daily_text(briefing))

    def _sign(self, timestamp: str) -> str:
        string_to_sign = f"{timestamp}\n{self.secret}"
        digest = hmac.new(
            string_to_sign.encode("utf-8"),
            b"",
            digestmod=hashlib.sha256,
        ).digest()
        return base64.b64encode(digest).decode("utf-8")

    def _build_daily_text(self, briefing: dict) -> str:
        date = briefing.get("date") or today_string(self.timezone)
        lines = [
            f"🌍 {briefing.get('title', '今日家庭全球简报')}｜{date}",
            "",
            f"一句话总结：{briefing.get('one_sentence_summary', '暂无明确总结。')}",
            "",
            "今日最重要的 5 件事：",
        ]

        for idx, item in enumerate((briefing.get("top_items") or [])[:5], start=1):
            title = item.get("title", "未命名事件")
            family_impact = item.get("family_impact", "影响不确定")
            lines.append(f"{idx}. {title}：{family_impact}")

        market = briefing.get("market_temperature") or {}
        lines.extend(
            [
                "",
                "今日投资温度：",
                f"美股：{market.get('us_stock', '不确定')}",
                f"A股：{market.get('a_share', '不确定')}",
                f"港股：{market.get('hk_stock', '不确定')}",
                f"黄金：{market.get('gold', '不确定')}",
                f"美元：{market.get('usd', '不确定')}",
                f"原油：{market.get('oil', '不确定')}",
                "",
                "给家人的提醒：",
            ]
        )
        family_action = briefing.get("family_action") or {}
        lines.append(family_action.get("summary", "今天没有必须马上行动的大事。不要因为单条新闻冲动投资。"))
        for warning in family_action.get("warnings", []) or []:
            lines.append(f"- {warning}")
        return truncate_text("\n".join(lines), 3000)
