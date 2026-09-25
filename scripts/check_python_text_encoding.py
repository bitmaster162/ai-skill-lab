#!/usr/bin/env python3
"""Prevent Python verifier text I/O from depending on the host locale."""
from __future__ import annotations

import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

errors: list[str] = []
checks = 0


def keyword_argument(call: ast.Call, name: str) -> ast.expr | None:
    for keyword in call.keywords:
        if keyword.arg == name:
            return keyword.value
    return None


def has_explicit_encoding(call: ast.Call, positional_index: int) -> bool:
    value = (
        call.args[positional_index]
        if len(call.args) > positional_index
        else keyword_argument(call, "encoding")
    )
    if value is None:
        return False
    return not (
        isinstance(value, ast.Constant)
        and value.value is None
    )


def text_mode(call: ast.Call) -> bool:
    mode = call.args[1] if len(call.args) > 1 else keyword_argument(call, "mode")
    if mode is None:
        return True
    if isinstance(mode, ast.Constant) and isinstance(mode.value, str):
        return "b" not in mode.value
    return True


for path in sorted(SCRIPTS.glob("*.py")):
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    relative = path.relative_to(ROOT).as_posix()

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        if isinstance(node.func, ast.Attribute) and node.func.attr == "read_text":
            checks += 1
            if not has_explicit_encoding(node, 0):
                errors.append(
                    f"{relative}:{node.lineno}: read_text requires explicit non-null encoding"
                )

        if isinstance(node.func, ast.Attribute) and node.func.attr == "write_text":
            checks += 1
            if not has_explicit_encoding(node, 1):
                errors.append(
                    f"{relative}:{node.lineno}: write_text requires explicit non-null encoding"
                )

        if isinstance(node.func, ast.Name) and node.func.id == "open":
            checks += 1
            if text_mode(node) and not has_explicit_encoding(node, 3):
                errors.append(
                    f"{relative}:{node.lineno}: text open() requires explicit non-null encoding"
                )

script_count = len(list(SCRIPTS.glob("*.py")))
print(f"python_text_encoding_checks={checks} scripts={script_count}")
if errors:
    print("PYTHON_TEXT_ENCODING_FAIL")
    for error in errors:
        print("FAIL:", error)
    sys.exit(1)

print("PYTHON_TEXT_ENCODING_PASS")
