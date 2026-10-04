#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from typing import Callable

USER_AGENT = "AI-Skill-Lab-P27.7-Monitor/1.1"
TIMEOUT_SECONDS = 15
RELAY_URL = "https://ai-skill-lab-lead-receiver.mirokonkr.workers.dev/r164/public-monitor/alert"
RELAY_SCHEMA = "ai-skill-lab.public-monitor-alert.v1"
RELAY_SIGNATURE_DOMAIN = "public-monitor-alert-v1"

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


def relay_payload(failures: list[Result], request_id: str) -> dict:
    return {
        "schema": RELAY_SCHEMA,
        "requestId": request_id,
        "failures": [
            {
                "name": item.name,
                "expected": item.expected,
                "actual": item.actual,
                "error": item.error,
            }
            for item in failures
        ],
    }


def send_monitor_alert(
    failures: list[Result],
    secret: str,
    timeout: int = TIMEOUT_SECONDS,
    now_seconds: int | None = None,
    request_id: str | None = None,
) -> bool:
    if not secret or len(secret.encode("utf-8")) < 32 or not failures:
        return False

    timestamp = str(now_seconds if now_seconds is not None else int(time.time()))
    rid = request_id or str(uuid.uuid4())
    body = json.dumps(relay_payload(failures, rid), separators=(",", ":"), sort_keys=True).encode("utf-8")
    digest = hmac.new(
        secret.encode("utf-8"),
        f"{RELAY_SIGNATURE_DOMAIN}.{timestamp}.{rid}.".encode("utf-8") + body,
        hashlib.sha256,
    ).hexdigest()

    request = urllib.request.Request(
        RELAY_URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
            "X-AI-Skill-Lab-Timestamp": timestamp,
            "X-AI-Skill-Lab-Request-Id": rid,
            "X-AI-Skill-Lab-Public-Monitor-Signature": f"v1={digest}",
        },
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

    secret = os.environ.get("PUBLIC_MONITOR_RELAY_SECRET", "")
    alert_sent = send_monitor_alert(failures, secret)
    print(
        "PUBLIC_MONITOR_FAIL "
        f"targets={len(results)} failures={len(failures)} relay_alert={'sent' if alert_sent else 'not_sent'}"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
