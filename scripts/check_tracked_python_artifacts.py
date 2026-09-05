#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TRACKED_FORBIDDEN = re.compile(r"(?:^|/)__pycache__(?:/|$)|\.py[co]$", re.IGNORECASE)
REQUIRED_IGNORE_RULES = ("__pycache__/", "*.py[cod]")

raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
tracked = [
    item.decode("utf-8", "surrogateescape").replace("\\", "/")
    for item in raw.split(b"\0")
    if item
]
forbidden = sorted(path for path in tracked if TRACKED_FORBIDDEN.search(path))
ignore_lines = set((ROOT / ".gitignore").read_text(encoding="utf-8").splitlines())
missing_rules = [rule for rule in REQUIRED_IGNORE_RULES if rule not in ignore_lines]

print(
    f"tracked_python_artifact_checks={len(tracked) + len(REQUIRED_IGNORE_RULES)} "
    f"tracked_files={len(tracked)} forbidden={len(forbidden)}"
)
if forbidden or missing_rules:
    print("TRACKED_PYTHON_ARTIFACT_QUARANTINE_FAIL")
    for path in forbidden:
        print("-", path)
    for rule in missing_rules:
        print("- missing .gitignore rule", rule)
    sys.exit(1)
print("TRACKED_PYTHON_ARTIFACT_QUARANTINE_PASS")
