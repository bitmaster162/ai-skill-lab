#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
WORKFLOW = ROOT / ".github" / "workflows" / "static-qa.yml"
PREFLIGHT = SCRIPTS / "preflight_release.py"
LEGACY_QUARANTINE = SCRIPTS / "check_legacy_qa_quarantine.py"

runtime_checks = sorted(path.name for path in SCRIPTS.glob("check_*runtime.mjs"))
workflow = WORKFLOW.read_text(encoding="utf-8")
preflight = PREFLIGHT.read_text(encoding="utf-8")
legacy = LEGACY_QUARANTINE.read_text(encoding="utf-8")
quarantined = {
    match.group(1)
    for match in re.finditer(r'"scripts/(check_[^"]*runtime\.mjs)"', legacy)
}

errors = []
missing_quarantined = quarantined.difference(runtime_checks)
for name in sorted(missing_quarantined):
    errors.append(f"{name}: declared quarantined but file is missing")

for name in runtime_checks:
    needle = f"scripts/{name}"
    workflow_count = workflow.count(needle)
    preflight_count = preflight.count(needle)
    if name in quarantined:
        if workflow_count != 0:
            errors.append(f"{name}: quarantined checker has workflow refs={workflow_count}, expected 0")
        if preflight_count != 0:
            errors.append(f"{name}: quarantined checker has preflight refs={preflight_count}, expected 0")
    else:
        if workflow_count != 1:
            errors.append(f"{name}: active checker workflow refs={workflow_count}, expected 1")
        if preflight_count != 1:
            errors.append(f"{name}: active checker preflight refs={preflight_count}, expected 1")

active_count = len(runtime_checks) - len(quarantined)
print(
    f"runtime_gate_inventory_checks={len(runtime_checks)} "
    f"active={active_count} quarantined={len(quarantined)}"
)
if errors:
    print("RUNTIME_GATE_INVENTORY_FAIL")
    for error in errors:
        print("FAIL:", error)
    raise SystemExit(1)
print("RUNTIME_GATE_INVENTORY_PASS")
