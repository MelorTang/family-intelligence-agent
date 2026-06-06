#!/usr/bin/env python3
"""Send stdin text to a Feishu custom bot webhook.

This is intentionally tiny and dependency-free because Hermes already handles
model choice, research, scheduling, and file operations.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.request


def build_sign(timestamp: str, secret: str) -> str:
    string_to_sign = f"{timestamp}\n{secret}"
    digest = hmac.new(string_to_sign.encode("utf-8"), b"", hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


def main() -> int:
    webhook_url = os.environ.get("FEISHU_WEBHOOK_URL", "").strip()
    secret = os.environ.get("FEISHU_SECRET", "").strip()
    text = sys.stdin.read().strip()

    if not webhook_url:
        print("FEISHU_WEBHOOK_URL is not set; skipped Feishu publishing.", file=sys.stderr)
        return 2
    if not text:
        print("No text received on stdin; skipped Feishu publishing.", file=sys.stderr)
        return 2

    payload: dict[str, object] = {
        "msg_type": "text",
        "content": {"text": text[:3000]},
    }
    if secret:
        timestamp = str(int(time.time()))
        payload["timestamp"] = timestamp
        payload["sign"] = build_sign(timestamp, secret)

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        print(f"Feishu publish failed: {exc}", file=sys.stderr)
        return 1

    print(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
