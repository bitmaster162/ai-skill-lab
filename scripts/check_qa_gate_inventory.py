#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
WORKFLOW = ROOT / ".github" / "workflows" / "static-qa.yml"
PREFLIGHT = SCRIPTS / "preflight_release.py"

QUARANTINED = {
    "check_capability_matrix.py": "check_legacy_qa_quarantine.py",
    "check_hero_engine.py": "check_legacy_qa_quarantine.py",
    "check_hero_engine_runtime.mjs": "check_legacy_qa_quarantine.py",
    "check-launch.mjs": "check_launch_quarantine.py",
}

check_names = sorted({
    path.name
    for pattern in ("check_*.py", "check_*.mjs", "check-*.mjs")
    for path in SCRIPTS.glob(pattern)
})
workflow = WORKFLOW.read_text(encoding="utf-8")
preflight = PREFLIGHT.read_text(encoding="utf-8")

errors = []

for name, owner_name in sorted(QUARANTINED.items()):
    path = SCRIPTS / name
    owner_path = SCRIPTS / owner_name
    if not path.is_file():
        errors.append(f"{name}: quarantined evidence file is missing")
        continue
    if not owner_path.is_file():
        errors.append(f"{name}: quarantine owner {owner_name} is missing")
        continue
    owner_text = owner_path.read_text(encoding="utf-8")
    if f"scripts/{name}" not in owner_text:
        errors.append(f"{name}: quarantine owner {owner_name} does not explicitly reference it")

for name in check_names:
    needle = f"scripts/{name}"
    workflow_count = workflow.count(needle)
    preflight_count = preflight.count(needle)
    if name in QUARANTINED:
        if workflow_count != 0:
            errors.append(f"{name}: quarantined checker has workflow refs={workflow_count}, expected 0")
        if preflight_count != 0:
            errors.append(f"{name}: quarantined checker has preflight refs={preflight_count}, expected 0")
    else:
        if workflow_count != 1:
            errors.append(f"{name}: active checker workflow refs={workflow_count}, expected 1")
        if preflight_count != 1:
            errors.append(f"{name}: active checker preflight refs={preflight_count}, expected 1")

undeclared = sorted(set(QUARANTINED).difference(check_names))
for name in undeclared:
    errors.append(f"{name}: quarantine declaration exists but checker was not discovered")

active_count = len(check_names) - len(QUARANTINED)
print(
    f"qa_gate_inventory_checks={len(check_names)} "
    f"active={active_count} quarantined={len(QUARANTINED)}"
)
if errors:
    print("QA_GATE_INVENTORY_FAIL")
    for error in errors:
        print("FAIL:", error)
    raise SystemExit(1)
print("QA_GATE_INVENTORY_PASS")
