#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "package.json"
LAUNCH = ROOT / "scripts/check-launch.mjs"
WORKFLOW = ROOT / ".github/workflows/static-qa.yml"
PREFLIGHT = ROOT / "scripts/preflight_release.py"
README = ROOT / "README.md"

EVIDENCE_MARKERS = [
    "NEXT_PUBLIC_SITE_URL",
    "NEXT_PUBLIC_TELEGRAM_URL",
    "LEAD_WEBHOOK_URL",
    "LEAD_WEBHOOK_SECRET",
    "LAUNCH_CHECK_PASS",
]
FORBIDDEN_PACKAGE_KEYS = {"check:launch", "build:launch"}
FORBIDDEN_LAUNCH_CALLS = ["check-launch.mjs", "npm run check:launch"]
README_REQUIRED_MARKERS = [
    "static-release",
    "python scripts/preflight_release.py --release",
]
EXPECTED_CORE_SCRIPTS = {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint .",
}

errors = []
checks = 0

checks += 1
if not LAUNCH.is_file():
    errors.append("ENV-bound launch checker evidence is missing")
    launch_text = ""
else:
    launch_text = LAUNCH.read_text(encoding="utf-8")

for marker in EVIDENCE_MARKERS:
    checks += 1
    if marker not in launch_text:
        errors.append(f"launch checker evidence marker missing {marker!r}")

package = json.loads(PACKAGE.read_text(encoding="utf-8"))
scripts = package.get("scripts")
checks += 1
if not isinstance(scripts, dict):
    errors.append("package.json scripts must be an object")
    scripts = {}

for key in sorted(FORBIDDEN_PACKAGE_KEYS):
    checks += 1
    if key in scripts:
        errors.append(f"package.json must not expose ENV-bound launch script {key!r}")

script_values = [str(value) for value in scripts.values()]
for marker in FORBIDDEN_LAUNCH_CALLS:
    checks += 1
    if any(marker in value for value in script_values):
        errors.append(f"package.json script value still invokes ENV-bound launch path {marker!r}")

for key, expected in EXPECTED_CORE_SCRIPTS.items():
    checks += 1
    if scripts.get(key) != expected:
        errors.append(f"package.json core script drift {key!r}: {scripts.get(key)!r} != {expected!r}")

workflow_text = WORKFLOW.read_text(encoding="utf-8")
preflight_text = PREFLIGHT.read_text(encoding="utf-8")
readme_text = README.read_text(encoding="utf-8")

for owner, text in [
    ("required workflow", workflow_text),
    ("release preflight", preflight_text),
    ("operator README", readme_text),
]:
    for marker in ["check-launch.mjs", "check:launch", "build:launch"]:
        checks += 1
        if marker in text:
            errors.append(f"{owner}: ENV-bound launch path must remain quarantined: {marker!r}")

for marker in README_REQUIRED_MARKERS:
    checks += 1
    if marker not in readme_text:
        errors.append(f"operator README required release-QA marker missing {marker!r}")

checks += 1
if workflow_text.count("python scripts/check_launch_quarantine.py") != 1:
    errors.append("required workflow must invoke launch quarantine exactly once")

checks += 1
if preflight_text.count('"scripts/check_launch_quarantine.py"') != 1:
    errors.append("release preflight must list launch quarantine exactly once")

print(
    f"launch_quarantine_checks={checks} package_scripts={len(scripts)} "
    f"evidence_markers={len(EVIDENCE_MARKERS)}"
)
if errors:
    for error in errors:
        print("FAIL:", error)
    sys.exit(1)
print("ENV_BOUND_LAUNCH_QUARANTINE_PASS")
