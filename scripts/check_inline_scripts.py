#!/usr/bin/env python3
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / 'deploy' / 'live'
JS_TYPES = {'text/javascript', 'application/javascript', 'module'}


class ScriptCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.scripts: list[tuple[str | None, str]] = []
        self._script_type: str | None = None
        self._parts: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != 'script':
            return
        if self._parts is not None:
            raise ValueError('nested script element')
        attr_map = {key.lower(): value for key, value in attrs}
        self._script_type = attr_map.get('type')
        self._parts = []

    def handle_data(self, data: str) -> None:
        if self._parts is not None:
            self._parts.append(data)

    def handle_entityref(self, name: str) -> None:
        if self._parts is not None:
            self._parts.append(f'&{name};')

    def handle_charref(self, name: str) -> None:
        if self._parts is not None:
            self._parts.append(f'&#{name};')

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != 'script' or self._parts is None:
            return
        self.scripts.append((self._script_type, ''.join(self._parts)))
        self._script_type = None
        self._parts = None

    def close(self) -> None:
        super().close()
        if self._parts is not None:
            raise ValueError('unterminated script element')


def collect_scripts(text: str) -> list[tuple[str | None, str]]:
    parser = ScriptCollector()
    parser.feed(text)
    parser.close()
    return parser.scripts


def main() -> int:
    total = 0
    checked = 0
    failures: list[str] = []
    for page in sorted(LIVE.rglob('*.html')):
        text = page.read_text(encoding='utf-8')
        try:
            scripts = collect_scripts(text)
        except ValueError as exc:
            failures.append(f'{page.relative_to(ROOT)}: {exc}')
            continue
        for idx, (script_type, body) in enumerate(scripts, 1):
            total += 1
            if script_type and script_type.lower() not in JS_TYPES:
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
