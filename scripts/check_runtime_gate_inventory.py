#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
WORKFLOW = ROOT / ".github" / "workflows" / "static-qa.yml"
PREFLIGHT = SCRIPTS / "preflight_release.py"

runtime_checks = sorted(path.name for path in SCRIPTS.glob("check_*runtime.mjs"))
workflow = WORKFLOW.read_text(encoding="utf-8")
preflight = PREFLIGHT.read_text(encoding="utf-8")

errors = []
for name in runtime_checks:
    needle = f"scripts/{name}"
    workflow_count = workflow.count(needle)
    preflight_count = preflight.count(needle)
    if workflow_count != 1:
        errors.append(f"{name}: workflow refs={workflow_count}, expected 1")
    if preflight_count != 1:
        errors.append(f"{name}: preflight refs={preflight_count}, expected 1")

print(f"runtime_gate_inventory_checks={len(runtime_checks)}")
if errors:
    print("RUNTIME_GATE_INVENTORY_FAIL")
    for error in errors:
        print("FAIL:", error)
    raise SystemExit(1)
print("RUNTIME_GATE_INVENTORY_PASS")
