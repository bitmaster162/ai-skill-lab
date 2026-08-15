#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import re, subprocess, sys, tempfile

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / 'deploy' / 'live'
SCRIPT_RE = re.compile(r'<script(?:\s[^>]*)?>(.*?)</script>', re.S | re.I)
TYPE_RE = re.compile(r'<script(?:\s[^>]*)?\btype=["\']([^"\']+)["\'][^>]*>', re.I)


def main() -> int:
    total = 0
    checked = 0
    failures: list[str] = []
    for page in sorted(LIVE.rglob('*.html')):
        text = page.read_text(encoding='utf-8')
        # preserve opening tag so JSON-LD/non-JS scripts can be skipped safely
        for idx, match in enumerate(re.finditer(r'(<script(?:\s[^>]*)?>)(.*?)</script>', text, re.S | re.I), 1):
            opening, body = match.group(1), match.group(2)
            total += 1
            tm = TYPE_RE.search(opening)
            if tm and tm.group(1).lower() not in {'text/javascript', 'application/javascript', 'module'}:
                continue
            checked += 1
            with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as fh:
                fh.write(body)
                tmp = Path(fh.name)
            try:
                proc = subprocess.run(['node', '--check', str(tmp)], capture_output=True, text=True)
            finally:
                tmp.unlink(missing_ok=True)
            if proc.returncode:
                detail = (proc.stderr or proc.stdout).strip().splitlines()
                failures.append(f'{page.relative_to(ROOT)} script#{idx}: {detail[-4] if len(detail)>=4 else detail[-1] if detail else "syntax error"}')
    print(f'inline_scripts_total={total} javascript_checked={checked}')
    if failures:
        for item in failures:
            print('FAIL:', item)
        return 1
    print('INLINE_SCRIPT_SYNTAX_PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
