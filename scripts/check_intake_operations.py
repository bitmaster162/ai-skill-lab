#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "services/lead-receiver-cloudflare/wrangler.jsonc"
INGRESS = ROOT / "services/lead-ingress/api/lead.js"
RECEIVER = ROOT / "services/lead-receiver-cloudflare/src/index.js"
WORKFLOW = ROOT / ".github/workflows/static-qa.yml"
PREFLIGHT = ROOT / "scripts/preflight_release.py"

errors = []
checks = 0

def require(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        errors.append(message)

cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
ingress = INGRESS.read_text(encoding="utf-8")
receiver = RECEIVER.read_text(encoding="utf-8")
workflow = WORKFLOW.read_text(encoding="utf-8")
preflight = PREFLIGHT.read_text(encoding="utf-8")

require(cfg.get("triggers") == {"crons": ["17 * * * *"]}, "receiver cron contract drift")
obs = cfg.get("observability") or {}
logs = obs.get("logs") or {}
traces = obs.get("traces") or {}
require(obs.get("enabled") is True, "receiver observability must be enabled")
require(logs.get("enabled") is True, "receiver logs must be enabled")
require(logs.get("invocation_logs") is True, "receiver invocation logs must be enabled")
require(logs.get("head_sampling_rate") == 1, "receiver log sampling must be 100%")
require(logs.get("persist") is True, "receiver logs must persist")
require(obs.get("redact_query_string") is True, "receiver query strings must be redacted")
require(traces.get("enabled") is False, "receiver traces must remain disabled")

require('const INTAKE_EVENT_SCHEMA = "ai-skill-lab.intake-event.v1";' in ingress, "ingress event schema missing")
require('const INGRESS_EVENT_FIELDS = new Set(["requestId", "status", "downstreamStatus"]);' in ingress, "ingress event allowlist drift")
require(ingress.count("console.") == 3, "ingress console calls must stay inside structured logger")
for event in ["forward_start", "downstream_error", "downstream_rejected", "forward_ok"]:
    require(f'logIngress(' in ingress and f'"{event}"' in ingress, f"ingress event missing {event}")

require('const INTAKE_EVENT_SCHEMA = "ai-skill-lab.intake-event.v1";' in receiver, "receiver event schema missing")
require('const RECEIVER_EVENT_FIELDS = new Set(["requestId", "status", "deleted"]);' in receiver, "receiver event allowlist drift")
require(receiver.count("console.") == 3, "receiver console calls must stay inside structured logger")
for event in ["rate_limit_error", "rate_limited", "db_error", "duplicate", "inserted", "retention_cleanup"]:
    require(f'logReceiver(' in receiver and f'"{event}"' in receiver, f"receiver event missing {event}")

for forbidden in ["payload }", "rawBody }", "secret }", "signatureRaw }", "contact }", "goal }"]:
    require(forbidden not in ingress and forbidden not in receiver, f"forbidden log-like payload marker {forbidden!r}")

receiver_test = "node --test services/lead-receiver-cloudflare/test/receiver.test.mjs"
operations_check = "python scripts/check_intake_operations.py"
require(workflow.count(receiver_test) == 1, "required static-release must test receiver exactly once")
require(workflow.count(operations_check) == 1, "required static-release must check intake operations exactly once")
require(preflight.count('["node", "--test", "services/lead-receiver-cloudflare/test/receiver.test.mjs"]') == 1, "preflight receiver test missing")
require(preflight.count('["python", "scripts/check_intake_operations.py"]') == 1, "preflight operations checker missing")

print(
    f"intake_operations_checks={checks} cron=17_minutely_hourly "
    f"observability=logs_only event_schema=ai-skill-lab.intake-event.v1"
)
if errors:
    for error in errors:
        print("FAIL:", error)
    sys.exit(1)
print("INTAKE_OPERATIONAL_CONTRACT_PASS")
