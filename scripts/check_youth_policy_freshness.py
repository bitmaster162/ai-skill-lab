#!/usr/bin/env python3
from datetime import date
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SURFACES = [
    "app/safety/page.tsx",
    "app/en/safety/page.tsx",
    "deploy/live/safety.html",
    "deploy/live/en/safety.html",
]
OFFICIAL_SOURCES = [
    "https://help.openai.com/en/articles/8313401",
    "https://help.openai.com/en/articles/12315553-parental-controls-on-chatgpt-faq/",
]
MAX_AGE_DAYS = 30
DATE_RE = re.compile(r'data-policy-verified=["\'](\d{4}-\d{2}-\d{2})["\']')

checks = 0
verified = {}

for rel in SURFACES:
    text = (ROOT / rel).read_text(encoding="utf-8")
    matches = DATE_RE.findall(text)
    if len(matches) != 1:
        print(f"YOUTH_POLICY_DATE_COUNT_FAIL {rel} count={len(matches)}")
        sys.exit(1)
    raw = matches[0]
    try:
        verified_date = date.fromisoformat(raw)
    except ValueError:
        print(f"YOUTH_POLICY_DATE_INVALID {rel} value={raw}")
        sys.exit(1)
    age = (date.today() - verified_date).days
    if age < 0:
        print(f"YOUTH_POLICY_DATE_FUTURE {rel} verified={raw} age_days={age}")
        sys.exit(1)
    if age > MAX_AGE_DAYS:
        print(f"YOUTH_POLICY_STALE {rel} verified={raw} age_days={age} max={MAX_AGE_DAYS}")
        sys.exit(1)
    verified[rel] = raw
    checks += 1
    for url in OFFICIAL_SOURCES:
        if url not in text:
            print(f"YOUTH_POLICY_SOURCE_MISSING {rel} {url}")
            sys.exit(1)
        checks += 1

dates = set(verified.values())
checks += 1
if len(dates) != 1:
    detail = ",".join(f"{rel}={value}" for rel, value in verified.items())
    print(f"YOUTH_POLICY_DATE_PARITY_FAIL {detail}")
    sys.exit(1)

verified_date = next(iter(dates))
age_days = (date.today() - date.fromisoformat(verified_date)).days
print(
    f"YOUTH_POLICY_FRESHNESS_PASS checks={checks} surfaces={len(SURFACES)} "
    f"verified={verified_date} age_days={age_days} max_age_days={MAX_AGE_DAYS}"
)
