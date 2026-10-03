#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Callable

USER_AGENT = "AI-Skill-Lab-P27.7-Monitor/1.0"
TIMEOUT_SECONDS = 15

TARGETS = (
    ("bitevo-home", "https://bitevo.work/", 200),
    ("bitevo-pricing", "https://bitevo.work/pricing", 200),
    ("bitevo-start", "https://bitevo.work/start", 200),
    ("aiskillab-home", "https://aiskillab.work/", 200),
    ("aiskillab-start", "https://aiskillab.work/start", 200),
)

@dataclass(frozen=True)
class Result:
    name: str
    url: str
    expected: int
    actual: int | None
    error: str | None = None


def fetch_get(url: str, timeout: int = TIMEOUT_SECONDS) -> int:
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return int(response.status)


def run_checks(fetcher: Callable[[str, int], int] = fetch_get) -> list[Result]:
    results: list[Result] = []
    for name, url, expected in TARGETS:
        try:
            actual = int(fetcher(url, TIMEOUT_SECONDS))
            error = None if actual == expected else f"unexpected_status={actual}"
        except urllib.error.HTTPError as exc:
            actual = int(exc.code)
            error = f"http_error={exc.code}"
        except Exception as exc:
            actual = None
            error = f"request_error={type(exc).__name__}"
        results.append(Result(name=name, url=url, expected=expected, actual=actual, error=error))
    return results


def format_alert(failures: list[Result]) -> str:
    lines = ["AI Skill Lab P27.7 public GET monitor failed."]
    for item in failures:
        observed = item.actual if item.actual is not None else item.error or "unknown"
        lines.append(f"- {item.name}: expected={item.expected} observed={observed} url={item.url}")
    return "\n".join(lines)


def send_telegram_alert(message: str, token: str, chat_id: str, timeout: int = TIMEOUT_SECONDS) -> bool:
    if not token or not chat_id:
        return False
    payload = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": message,
        "disable_web_page_preview": "true",
    }).encode("utf-8")
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return 200 <= int(response.status) < 300
    except Exception:
        return False


def main() -> int:
    results = run_checks()
    failures = [item for item in results if item.error is not None]
    for item in results:
        observed = item.actual if item.actual is not None else item.error or "unknown"
        print(f"PUBLIC_MONITOR_TARGET name={item.name} method=GET expected={item.expected} observed={observed}")

    if not failures:
        print(f"PUBLIC_MONITOR_PASS targets={len(results)} method=GET post_forms=0")
        return 0

    token = os.environ.get("PUBLIC_MONITOR_TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("PUBLIC_MONITOR_TELEGRAM_CHAT_ID", "")
    alert_sent = send_telegram_alert(format_alert(failures), token, chat_id)
    print(
        "PUBLIC_MONITOR_FAIL "
        f"targets={len(results)} failures={len(failures)} telegram_alert={'sent' if alert_sent else 'not_sent'}"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
