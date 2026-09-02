#!/usr/bin/env python3
from __future__ import annotations

import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "scripts/verify_live_static.py"
WORKFLOW = ROOT / ".github/workflows/static-qa.yml"
PREFLIGHT = ROOT / "scripts/preflight_release.py"

EXPECTED_EXACT_HOSTS = {"ai-skill-lab.vercel.app"}
EXPECTED_HOST_SUFFIXES = ("-bitevo-s-projects.vercel.app",)

errors = []
checks = 0

verifier_text = VERIFIER.read_text(encoding="utf-8")
workflow_text = WORKFLOW.read_text(encoding="utf-8")
preflight_text = PREFLIGHT.read_text(encoding="utf-8")

required_markers = [
    "urlsplit",
    "HTTPRedirectHandler",
    "build_opener",
    "SafeRedirectHandler",
    "validate_target_url(args.base_url, require_root=True)",
    "validate_target_url(newurl)",
    "validate_target_url(url)",
    "OPENER.open(",
]
for marker in required_markers:
    checks += 1
    if marker not in verifier_text:
        errors.append(f"live verifier missing target-safety marker {marker!r}")

for marker in [
    "urlopen(",
    "http://",
    ".write_text(",
    ".write_bytes(",
    ".mkdir(",
    ".unlink(",
]:
    checks += 1
    if marker in verifier_text:
        errors.append(f"live verifier contains forbidden marker {marker!r}")

tree = ast.parse(verifier_text, filename=str(VERIFIER))
assignments = {}
for node in tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in {
                "ALLOWED_EXACT_HOSTS",
                "ALLOWED_HOST_SUFFIXES",
            }:
                assignments[target.id] = ast.literal_eval(node.value)

checks += 1
if assignments.get("ALLOWED_EXACT_HOSTS") != EXPECTED_EXACT_HOSTS:
    errors.append(
        "live verifier exact-host allowlist drift "
        f"{assignments.get('ALLOWED_EXACT_HOSTS')!r}"
    )

checks += 1
if assignments.get("ALLOWED_HOST_SUFFIXES") != EXPECTED_HOST_SUFFIXES:
    errors.append(
        "live verifier host-suffix allowlist drift "
        f"{assignments.get('ALLOWED_HOST_SUFFIXES')!r}"
    )

checks += 1
if "verify_live_static.py" in workflow_text:
    errors.append("required static-release workflow must not invoke network-bound live verifier")

checks += 1
if "verify_live_static.py" in preflight_text:
    errors.append("release preflight must not invoke network-bound live verifier")

checks += 1
if workflow_text.count("python scripts/check_live_verifier_safety.py") != 1:
    errors.append("required workflow must invoke live verifier safety checker exactly once")

checks += 1
if preflight_text.count('"scripts/check_live_verifier_safety.py"') != 1:
    errors.append("release preflight must list live verifier safety checker exactly once")

print(
    f"live_verifier_safety_checks={checks} "
    f"allowed_exact={len(EXPECTED_EXACT_HOSTS)} "
    f"allowed_suffixes={len(EXPECTED_HOST_SUFFIXES)}"
)
if errors:
    for error in errors:
        print("FAIL:", error)
    sys.exit(1)
print("LIVE_VERIFIER_TARGET_SAFETY_PASS")
