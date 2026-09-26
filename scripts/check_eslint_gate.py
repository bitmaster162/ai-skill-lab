#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ESLINT = ROOT / "node_modules" / "eslint" / "bin" / "eslint.js"


def main() -> int:
    if not ESLINT.is_file():
        print("ESLINT_GATE_FAIL missing node_modules/eslint/bin/eslint.js; run locked npm ci first")
        return 1
    result = subprocess.run(
        ["node", str(ESLINT), "."],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(result.stderr, end="" if result.stderr.endswith("\n") else "\n", file=sys.stderr)
    if result.returncode != 0:
        print(f"ESLINT_GATE_FAIL returncode={result.returncode}")
        return result.returncode
    print("ESLINT_GATE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
