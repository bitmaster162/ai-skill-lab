#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import importlib.util
from io import StringIO
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "scripts" / "lead_inbox.py"
SPEC = importlib.util.spec_from_file_location("lead_inbox", TARGET)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load lead_inbox.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)

errors: list[str] = []
checks = 0


def require(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        errors.append(message)


source = TARGET.read_text(encoding="utf-8")
for field in ["name", "contact", "goal"]:
    require(field not in MOD.LIST_FIELDS.split(", "), f"list metadata leaks {field}")
    require(field in MOD.SHOW_FIELDS.split(", "), f"show view missing {field}")

list_sql = MOD.build_list_sql(20, 168)
require(list_sql.startswith("SELECT "), "list query must be SELECT")
require("ORDER BY received_at DESC LIMIT 20" in list_sql, "list ordering/limit drift")
for field in ["name", "contact", "goal"]:
    require(field not in list_sql, f"list SQL leaks {field}")

request_id = "f375ba94-372f-465b-9f22-3b3d6fbff7f8"
show_sql = MOD.build_show_sql(request_id)
require(show_sql.startswith("SELECT "), "show query must be SELECT")
require(f"request_id = '{request_id}'" in show_sql, "show query request-id drift")
for field in ["name", "contact", "goal"]:
    require(field in show_sql, f"show SQL missing {field}")

require(MOD.UUID_V4.fullmatch(request_id) is not None, "known UUIDv4 rejected")
for invalid in ["", "not-a-uuid", "00000000-0000-1000-8000-000000000000"]:
    try:
        MOD.build_show_sql(invalid)
    except ValueError:
        pass
    else:
        errors.append(f"invalid request-id accepted: {invalid!r}")
    checks += 1
for sql in [
    "DELETE FROM lead_intake_r101b;",
    "UPDATE lead_intake_r101b SET goal='x';",
    "INSERT INTO lead_intake_r101b(request_id) VALUES ('x');",
    "SELECT request_id FROM lead_intake_r101b; DELETE FROM lead_intake_r101b;",
    "PRAGMA table_info(lead_intake_r101b);",
]:
    try:
        MOD.assert_read_only_sql(sql)
    except ValueError:
        pass
    else:
        errors.append(f"unsafe SQL accepted: {sql}")
    checks += 1

require("LEAD_WEBHOOK_SECRET" not in source, "operator inbox must not reference webhook secret")
require("os.environ" not in source and "os.getenv" not in source, "operator inbox must not read environment secrets")
require('"--remote", "--command", sql, "--json"' in source, "Wrangler read contract drift")

sample = [{
    "request_id": request_id, "received_at": "2026-09-12T00:00:00.000Z",
    "audience": "business", "locale": "en", "program": "", "source_path": "/en/start",
}]
buffer = StringIO()
with contextlib.redirect_stdout(buffer):
    MOD.print_list(sample, False)
rendered = buffer.getvalue()
require(request_id in rendered and "business" in rendered, "list rendering lost metadata")
require("name" not in rendered and "contact" not in rendered and "goal" not in rendered,
        "list rendering unexpectedly exposes PII fields")

workflow = (ROOT / ".github" / "workflows" / "static-qa.yml").read_text(encoding="utf-8")
preflight = (ROOT / "scripts" / "preflight_release.py").read_text(encoding="utf-8")
command = "python scripts/check_lead_inbox.py"
require(workflow.count(command) == 1, "required static-release must check lead inbox exactly once")
require(preflight.count('["python", "scripts/check_lead_inbox.py"]') == 1,
        "preflight must check lead inbox exactly once")

print(f"lead_inbox_checks={checks} list_pii=excluded show_requires=uuidv4 sql=select_only")
if errors:
    for error in errors:
        print("FAIL:", error)
    sys.exit(1)
print("LEAD_INBOX_CONTRACT_PASS")
