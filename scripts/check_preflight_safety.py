#!/usr/bin/env python3
from __future__ import annotations

import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "scripts/preflight_release.py"
WORKFLOW = ROOT / ".github/workflows/static-qa.yml"
PUBLIC_ORIGIN_HELPER = ROOT / "scripts/public_origin.py"

FORBIDDEN = [
    "build_csp.py",
    "build_static_manifest.py",
    "build_release_artifacts.py",
    "check:launch",
    "check-launch.mjs",
    "NEXT_PUBLIC_SITE_URL",
    "NEXT_PUBLIC_TELEGRAM_URL",
    ".write_text(",
    ".write_bytes(",
    ".mkdir(",
    ".unlink(",
    "shutil.",
]
errors = []
checks = 0

preflight_text = PREFLIGHT.read_text(encoding="utf-8")
workflow_text = WORKFLOW.read_text(encoding="utf-8")
public_origin_text = PUBLIC_ORIGIN_HELPER.read_text(encoding="utf-8")

for marker in FORBIDDEN:
    checks += 1
    if marker in preflight_text:
        errors.append(f"preflight contains forbidden mutating/env-bound marker {marker!r}")


for marker in ("NEXT_PUBLIC_SITE_URL", "import os", "from os import"):
    checks += 1
    if marker in public_origin_text:
        errors.append(f"public_origin.py contains forbidden ENV-bound marker {marker!r}")

checks += 1
if "PUBLIC_ORIGIN = normalize_public_origin(DEFAULT_PUBLIC_ORIGIN)" not in public_origin_text:
    errors.append("public_origin.py must bind static QA to DEFAULT_PUBLIC_ORIGIN")

checks += 1
if "check-launch.mjs" in workflow_text or "check:launch" in workflow_text:
    errors.append("required static-release workflow must not invoke ENV-bound launch check")

tree = ast.parse(preflight_text, filename=str(PREFLIGHT))
checks_node = None
for node in tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "CHECKS":
                checks_node = node.value
                break
    if checks_node is not None:
        break

checks += 1
if checks_node is None:
    errors.append("preflight CHECKS literal is missing")
    preflight_commands = []
else:
    try:
        entries = ast.literal_eval(checks_node)
    except (ValueError, TypeError, SyntaxError) as exc:
        errors.append(f"preflight CHECKS is not a literal: {exc}")
        entries = []
    preflight_commands = [" ".join(command) for _name, command in entries]

workflow_commands = []
for raw in workflow_text.splitlines():
    stripped = raw.strip()
    if stripped.startswith("run: "):
        command = stripped[5:].strip()
        if command.startswith(("python ", "node ")):
            workflow_commands.append(command)

checks += 1
if len(preflight_commands) != len(set(preflight_commands)):
    errors.append("preflight CHECKS contains duplicate commands")

checks += 1
if len(workflow_commands) != len(set(workflow_commands)):
    errors.append("workflow contains duplicate python/node commands")

checks += 1
if preflight_commands != workflow_commands:
    missing = [command for command in workflow_commands if command not in preflight_commands]
    extra = [command for command in preflight_commands if command not in workflow_commands]
    errors.append(f"preflight/workflow command drift missing={missing} extra={extra}")

checks += 1
if '["git", "diff", "--check"]' not in preflight_text:
    errors.append("preflight must retain read-only git diff check")

checks += 1
if "ai-skill-lab.preflight.v2" not in preflight_text:
    errors.append("preflight receipt schema must be v2")

checks += 1
if "--output" in preflight_text:
    errors.append("preflight must not expose a file-output option")

print(
    f"preflight_safety_checks={checks} workflow_commands={len(workflow_commands)} "
    f"preflight_commands={len(preflight_commands)}"
)
if errors:
    for error in errors:
        print("FAIL:", error)
    sys.exit(1)
print("RELEASE_PREFLIGHT_SAFETY_PASS")
