#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
FACTS = ROOT / "services/lead-ingress/faq_facts.json"
BOT = ROOT / "services/lead-ingress/api/telegram-faq.js"
LEAD = ROOT / "services/lead-ingress/api/lead.js"
ENV_EXAMPLE = ROOT / "services/lead-ingress/.env.example"
WORKFLOW = ROOT / ".github/workflows/static-qa.yml"
PREFLIGHT = ROOT / "scripts/preflight_release.py"
RU_FAQ = ROOT / "app/(ru)/faq/page.tsx"
EN_FAQ = ROOT / "app/(en)/en/faq/page.tsx"

errors: list[str] = []
checks = 0

def require(value: bool, message: str) -> None:
    global checks
    checks += 1
    if not value:
        errors.append(message)

def source_items(text: str) -> list[list[str]]:
    return [list(item) for item in re.findall(r'\["([^"]+\?)",\s*"([^"]*)"\]', text)]

facts = json.loads(FACTS.read_text(encoding="utf-8"))
bot = BOT.read_text(encoding="utf-8")
lead = LEAD.read_text(encoding="utf-8")
env = ENV_EXAMPLE.read_text(encoding="utf-8")
workflow = WORKFLOW.read_text(encoding="utf-8")
preflight = PREFLIGHT.read_text(encoding="utf-8")
ru_source = source_items(RU_FAQ.read_text(encoding="utf-8"))
en_source = source_items(EN_FAQ.read_text(encoding="utf-8"))

require(facts.get("schema") == "ai-skill-lab.telegram-faq.v1", "FAQ facts schema drift")
require(facts.get("version") == 1, "FAQ facts version drift")
require(facts.get("ru") == ru_source, "RU Telegram FAQ must exactly match published FAQ source")
require(facts.get("en") == en_source, "EN Telegram FAQ must exactly match published FAQ source")
require(len(ru_source) == 11 and len(en_source) == 11, "FAQ source must remain 11 RU + 11 EN")
require(facts.get("booking_path") == "https://aiskillab.work/start", "booking path must remain canonical Start")
require(facts.get("privacy_path") == "https://aiskillab.work/privacy", "privacy path must remain canonical")

for marker in [
    'TELEGRAM_FAQ_ENABLED',
    'TELEGRAM_FAQ_BOT_TOKEN',
    'TELEGRAM_FAQ_WEBHOOK_SECRET',
    'x-telegram-bot-api-secret-token',
    'handleLead',
    'acceptDuplicate: true',
    'telegram-update-v1:',
    'telegram-user-v1:',
    'sourcePath: "/telegram-faq"',
    'privacyConsent: "yes"',
    'https://aiskillab.work/api/lead',
]:
    require(marker in bot, f"Telegram FAQ bot contract marker missing: {marker}")

require("OPENROUTER" not in bot, "F1.5 FAQ bot must remain deterministic and must not call OpenRouter")
require("chat/completions" not in bot, "F1.5 FAQ bot must not contain model endpoint")
require(bot.count("console.") == 3, "Telegram FAQ custom logging must stay inside one structured logger")
require('const LOG_FIELDS = new Set(["updateId", "status", "action"]);' in bot, "Telegram FAQ log allowlist drift")
for forbidden in ["message.text }", "username }", "chatId }", "goal }", "BOT_TOKEN }", "WEBHOOK_SECRET }"]:
    require(forbidden not in bot, f"forbidden log-like payload marker {forbidden!r}")

require('TELEGRAM_FAQ_ENABLED=false' in env, "Telegram FAQ activation must default false")
require(re.search(r"(?m)^TELEGRAM_FAQ_BOT_TOKEN=$", env) is not None, "Telegram bot token example must be blank")
require(re.search(r"(?m)^TELEGRAM_FAQ_WEBHOOK_SECRET=$", env) is not None, "Telegram webhook secret example must be blank")

for marker in [
    "internal = {}",
    "internal.requestId",
    "internal.ipToken",
    "internal.acceptDuplicate === true",
    "TOKEN_HEX_64",
    "UUID_V4",
]:
    require(marker in lead, f"lead handler trusted internal contract missing: {marker}")

test_command = "node --test services/lead-ingress/test/telegram-faq.test.mjs"
check_command = "python scripts/check_telegram_faq_bot.py"
require(workflow.count(test_command) == 1, "static-release must run Telegram FAQ tests exactly once")
require(workflow.count(check_command) == 1, "static-release must run Telegram FAQ contract checker exactly once")
require(preflight.count('["node", "--test", "services/lead-ingress/test/telegram-faq.test.mjs"]') == 1, "preflight Telegram FAQ test missing")
require(preflight.count('["python", "scripts/check_telegram_faq_bot.py"]') == 1, "preflight Telegram FAQ checker missing")

print(
    f"telegram_faq_bot_checks={checks} faq_ru={len(ru_source)} faq_en={len(en_source)} "
    "model_calls=0 activation_default=OFF lead_reuse=YES"
)
if errors:
    print("TELEGRAM_FAQ_BOT_CONTRACT_FAIL")
    for error in errors:
        print("FAIL:", error)
    raise SystemExit(1)
print("TELEGRAM_FAQ_BOT_CONTRACT_PASS")
