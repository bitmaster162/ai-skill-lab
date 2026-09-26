#!/usr/bin/env python3
from __future__ import annotations

import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "scripts/preflight_release.py"
WORKFLOW = ROOT / ".github/workflows/static-qa.yml"
PUBLIC_ORIGIN_HELPER = ROOT / "scripts/public_origin.py"
README = ROOT / "README.md"
WORKFLOW_DIR = ROOT / ".github" / "workflows"

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
readme_text = README.read_text(encoding="utf-8")
locked_install_command = "npm ci --ignore-scripts --audit=false --fund=false"
local_preflight_command = "python scripts/preflight_release.py --release <receipt-label>"
workflow_files = sorted(WORKFLOW_DIR.glob("*.yml"))

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

checks += 1
if len(workflow_files) != 3:
    errors.append(f"workflow inventory drift expected=3 actual={len(workflow_files)}")
for workflow_path in workflow_files:
    workflow_source = workflow_path.read_text(encoding="utf-8")
    checks += 1
    if "ubuntu-latest" in workflow_source:
        errors.append(f"{workflow_path.name}: floating ubuntu-latest runner is forbidden")
    checks += 1
    if workflow_source.count("runs-on: ubuntu-24.04") != 1:
        errors.append(f"{workflow_path.name}: expected exactly one ubuntu-24.04 runner binding")

checks += 1
if readme_text.count(locked_install_command) != 1:
    errors.append("README must contain the locked npm install command exactly once")
checks += 1
if readme_text.count(local_preflight_command) != 1:
    errors.append("README must contain the local preflight command exactly once")
checks += 1
if locked_install_command in readme_text and local_preflight_command in readme_text:
    if readme_text.index(locked_install_command) > readme_text.index(local_preflight_command):
        errors.append("README must install locked npm dependencies before local preflight")

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

main_node = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main"), None)
checks += 1
if main_node is None:
    errors.append("preflight main() is missing")
else:
    identity_index = None
    gate_loop_index = None
    canonical_receipt = False
    for idx, node in enumerate(main_node.body):
        if isinstance(node, ast.Try):
            for stmt in node.body:
                if isinstance(stmt, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "release" for t in stmt.targets):
                    call = stmt.value
                    if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == "require_release_identity":
                        identity_index = idx
        if isinstance(node, ast.For) and isinstance(node.iter, ast.Name) and node.iter.id == "CHECKS":
            gate_loop_index = idx
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "receipt" for t in node.targets) and isinstance(node.value, ast.Dict):
            for key, value in zip(node.value.keys, node.value.values):
                if isinstance(key, ast.Constant) and key.value == "release" and isinstance(value, ast.Name) and value.id == "release":
                    canonical_receipt = True
    checks += 1
    if identity_index is None or gate_loop_index is None or identity_index >= gate_loop_index:
        errors.append("release identity validation must occur before CHECKS gate loop")
    checks += 1
    if not canonical_receipt:
        errors.append("preflight receipt must use canonical validated release variable")
checks += 1
if 'RELEASE_PREFLIGHT_IDENTITY_FAIL' not in preflight_text or 'return 2' not in preflight_text:
    errors.append("preflight identity mismatch must retain explicit fail-closed marker and exit code 2")

print(
    f"preflight_safety_checks={checks} workflow_commands={len(workflow_commands)} "
    f"preflight_commands={len(preflight_commands)}"
)
if errors:
    for error in errors:
        print("FAIL:", error)
    sys.exit(1)
print("RELEASE_PREFLIGHT_SAFETY_PASS")
