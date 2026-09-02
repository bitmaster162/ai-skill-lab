#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/static-qa.yml"
PREFLIGHT = ROOT / "scripts/preflight_release.py"
PACKAGE = ROOT / "package.json"
README = ROOT / "README.md"

LEGACY_CHECKERS = {
    "scripts/check_capability_matrix.py": "AI Capability Matrix",
    "scripts/check_hero_engine.py": '<HeroEngine',
    "scripts/check_hero_engine_runtime.mjs": "[data-engine-key]",
}

READINESS_ARCHIVE_REQUIRED_MARKERS = [
    "Root-level `R*_READINESS.md` files are historical evidence snapshots from earlier release epochs.",
    "They are not current operator instructions, release authority, production-state authority, or approval to run legacy commands.",
    "Do not execute commands or rely on deployment/status claims from those files as current truth.",
    "Current repository release authority is the required `static-release` workflow and the local read-only preflight above.",
]

errors = []
checks = 0

workflow_text = WORKFLOW.read_text(encoding="utf-8")
preflight_text = PREFLIGHT.read_text(encoding="utf-8")
package_text = PACKAGE.read_text(encoding="utf-8")
readme_text = README.read_text(encoding="utf-8")
readiness_files = sorted(ROOT.glob("R*_READINESS.md"))

checks += 1
if not readiness_files:
    errors.append("historical readiness evidence snapshots are missing")

for marker in READINESS_ARCHIVE_REQUIRED_MARKERS:
    checks += 1
    if marker not in readme_text:
        errors.append(f"README: historical readiness authority boundary marker missing {marker!r}")

for owner, owner_text in [
    ("required workflow", workflow_text),
    ("release preflight", preflight_text),
    ("package scripts", package_text),
]:
    checks += 1
    if any(path.name in owner_text for path in readiness_files):
        errors.append(f"{owner}: historical readiness snapshot must remain outside current release authority")

for rel, evidence_marker in LEGACY_CHECKERS.items():
    path = ROOT / rel
    checks += 1
    if not path.is_file():
        errors.append(f"legacy checker evidence missing: {rel}")
        continue
    text = path.read_text(encoding="utf-8")
    checks += 1
    if evidence_marker not in text:
        errors.append(f"{rel}: legacy evidence marker missing {evidence_marker!r}")
    for owner, owner_text in [
        ("required workflow", workflow_text),
        ("release preflight", preflight_text),
        ("package scripts", package_text),
    ]:
        checks += 1
        if rel in owner_text:
            errors.append(f"{owner}: legacy checker must remain quarantined: {rel}")

source_homes = {
    "app/page.tsx": '<R77CommercialHome locale="ru" />',
    "app/en/page.tsx": '<R77CommercialHome locale="en" />',
}
for rel, mount in source_homes.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    checks += 1
    if mount not in text:
        errors.append(f"{rel}: current R77 home mount missing")
    for forbidden in ["HeroEngine", "AI Capability Matrix"]:
        checks += 1
        if forbidden in text:
            errors.append(f"{rel}: legacy home surface reintroduced {forbidden!r}")

for rel in ["deploy/live/index.html", "deploy/live/en.html"]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    checks += 1
    if "r77-commercial.css" not in text:
        errors.append(f"{rel}: R77 commercial static surface missing")
    for forbidden in [
        "data-hero-engine",
        "data-engine-key=",
        "AI SKILL ENGINE",
        "AI Capability Matrix",
    ]:
        checks += 1
        if forbidden in text:
            errors.append(f"{rel}: legacy static home surface reintroduced {forbidden!r}")

checks += 1
if workflow_text.count("python scripts/check_legacy_qa_quarantine.py") != 1:
    errors.append("required workflow must invoke legacy QA quarantine exactly once")

checks += 1
if preflight_text.count('"scripts/check_legacy_qa_quarantine.py"') != 1:
    errors.append("release preflight must list legacy QA quarantine exactly once")

print(
    f"legacy_qa_quarantine_checks={checks} legacy_checkers={len(LEGACY_CHECKERS)} "
    f"home_surfaces={len(source_homes) + 2} readiness_snapshots={len(readiness_files)}"
)
if errors:
    for error in errors:
        print("FAIL:", error)
    sys.exit(1)
print("LEGACY_QA_QUARANTINE_PASS")
