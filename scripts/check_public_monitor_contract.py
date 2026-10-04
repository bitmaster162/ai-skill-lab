#!/usr/bin/env python3
from __future__ import annotations

import ast
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/public-monitor.yml"
MONITOR = ROOT / "scripts/public_monitor.py"
TEST = ROOT / "scripts/test_public_monitor.py"
WORKER = ROOT / "services/lead-receiver-cloudflare/src/index.js"
RELAY_TEST = ROOT / "services/lead-receiver-cloudflare/test/public-monitor-relay.test.mjs"
STATIC_QA = ROOT / ".github/workflows/static-qa.yml"
PREFLIGHT = ROOT / "scripts/preflight_release.py"

EXPECTED = [
    ("bitevo-home", "https://bitevo.work/", 200),
    ("bitevo-pricing", "https://bitevo.work/pricing", 200),
    ("bitevo-start", "https://bitevo.work/start", 200),
    ("aiskillab-home", "https://aiskillab.work/", 200),
    ("aiskillab-start", "https://aiskillab.work/start", 200),
]

errors: list[str] = []
checks = 0

def require(value: bool, message: str) -> None:
    global checks
    checks += 1
    if not value:
        errors.append(message)

workflow = WORKFLOW.read_text(encoding="utf-8")
monitor = MONITOR.read_text(encoding="utf-8")
worker = WORKER.read_text(encoding="utf-8")
static_qa = STATIC_QA.read_text(encoding="utf-8")
preflight = PREFLIGHT.read_text(encoding="utf-8")

require("cron: '*/30 * * * *'" in workflow or 'cron: "*/30 * * * *"' in workflow, "monitor schedule must be every 30 minutes")
require("if: ${{ vars.PUBLIC_MONITOR_ENABLED == 'true' }}" in workflow, "monitor activation must default off unless explicitly enabled by repo variable")
require("runs-on: ubuntu-24.04" in workflow, "monitor must use pinned ubuntu-24.04 runner")
require("actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1" in workflow, "checkout action must be pinned")
require("actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97" in workflow, "setup-python action must be pinned")
require("permissions:\n  contents: read" in workflow, "monitor permissions must remain contents read only")
require("pull_request:" not in workflow and re.search(r"(?m)^\s+push:", workflow) is None, "scheduled monitor must not run on PR/push")
require("python scripts/public_monitor.py" in workflow, "scheduled job must run public monitor")
require("PUBLIC_MONITOR_RELAY_SECRET" in workflow, "dedicated monitor relay secret binding missing")
require("PUBLIC_MONITOR_TELEGRAM_BOT_TOKEN" not in workflow, "GitHub workflow must not receive BotFather token")
require("PUBLIC_MONITOR_TELEGRAM_CHAT_ID" not in workflow, "GitHub workflow must not receive owner Telegram chat id")

tree = ast.parse(monitor, filename=str(MONITOR))
targets = None
for node in tree.body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "TARGETS" for t in node.targets):
        targets = ast.literal_eval(node.value)
        break
require(list(targets or []) == EXPECTED, f"target inventory drift: {targets!r}")
require(monitor.count('method="GET"') == 1, "monitored site fetch must use one explicit GET request constructor")
require("urllib.request.urlopen(request" in monitor, "monitor must execute explicit request object")
require('RELAY_URL = "https://ai-skill-lab-lead-receiver.mirokonkr.workers.dev/r164/public-monitor/alert"' in monitor, "fixed Cloudflare relay endpoint missing")
require('RELAY_SCHEMA = "ai-skill-lab.public-monitor-alert.v1"' in monitor, "relay schema missing")
require('RELAY_SIGNATURE_DOMAIN = "public-monitor-alert-v1"' in monitor, "relay HMAC domain missing")
require("api.telegram.org" not in monitor, "GitHub monitor must never call Telegram directly")
require("PUBLIC_MONITOR_TELEGRAM_BOT_TOKEN" not in monitor, "monitor must not read BotFather token")
require("PUBLIC_MONITOR_TELEGRAM_CHAT_ID" not in monitor, "monitor must not read owner Telegram chat id")
require(monitor.count('method="POST"') == 1, "only signed Cloudflare alert relay may use POST")
require("/api/lead" not in monitor and "/api/route" not in monitor, "monitor must never POST to application or route endpoints")
require("PUBLIC_MONITOR_PASS" in monitor and "PUBLIC_MONITOR_FAIL" in monitor, "monitor receipts missing")
require("return 1" in monitor, "monitor failures must fail the job")

require('const PUBLIC_MONITOR_ALERT_PATH = "/r164/public-monitor/alert";' in worker, "Worker monitor relay route missing")
require('const PUBLIC_MONITOR_ALERT_SCHEMA = "ai-skill-lab.public-monitor-alert.v1";' in worker, "Worker monitor relay schema missing")
require('const PUBLIC_MONITOR_SIGNATURE_DOMAIN = "public-monitor-alert-v1";' in worker, "Worker monitor relay HMAC domain missing")
require('env?.PUBLIC_MONITOR_RELAY_ENABLED !== "true"' in worker, "Worker monitor relay must fail closed")
require("PUBLIC_MONITOR_RELAY_SECRET" in worker, "Worker monitor relay secret missing")
require("LEAD_NOTIFY_BOT_TOKEN" in worker and "LEAD_NOTIFY_CHAT_ID" in worker, "Worker must reuse existing owner notification bindings")
require("PUBLIC_MONITOR_TARGET_URLS" in worker, "Worker must own canonical target URL map")
require("public_monitor_alert_sent" in worker and "public_monitor_alert_failed" in worker, "Worker monitor relay receipts missing")

test_command = "python scripts/test_public_monitor.py"
check_command = "python scripts/check_public_monitor_contract.py"
relay_test_command = "node --test services/lead-receiver-cloudflare/test/public-monitor-relay.test.mjs"
require(static_qa.count(test_command) == 1, "static QA monitor unit test missing")
require(static_qa.count(check_command) == 1, "static QA monitor contract check missing")
require(static_qa.count(relay_test_command) == 1, "static QA Worker monitor relay test missing")
require(preflight.count('["python", "scripts/test_public_monitor.py"]') == 1, "preflight monitor unit test missing")
require(preflight.count('["python", "scripts/check_public_monitor_contract.py"]') == 1, "preflight monitor contract checker missing")
require(preflight.count('["node", "--test", "services/lead-receiver-cloudflare/test/public-monitor-relay.test.mjs"]') == 1, "preflight Worker monitor relay test missing")
require(TEST.is_file(), "monitor unit test file missing")
require(RELAY_TEST.is_file(), "Worker monitor relay test file missing")

print(
    f"public_monitor_contract_checks={checks} targets={len(EXPECTED)} "
    "schedule=30m site_methods=GET alert_transport=SIGNED_CLOUDFLARE_RELAY bot_token_copy=NO"
)
if errors:
    print("PUBLIC_MONITOR_CONTRACT_FAIL")
    for error in errors:
        print("FAIL:", error)
    raise SystemExit(1)
print("PUBLIC_MONITOR_CONTRACT_PASS")
