from __future__ import annotations
from pathlib import Path
import re

IMPORT_RE = re.compile(r'@import\s+(?:url\()?["\']?([^"\')\s;]+)', re.I)
EXTERNAL_RE = re.compile(r'^[a-z][a-z0-9+.-]*:|^//', re.I)

def read_local_css_graph(entry: Path, live_root: Path) -> str:
    live = live_root.resolve()
    seen: set[Path] = set()
    parts: list[str] = []

    def walk(path: Path) -> None:
        path = path.resolve()
        if path in seen:
            return
        if path != live and live not in path.parents:
            raise ValueError(f'CSS import escapes live root: {path}')
        if not path.is_file():
            raise ValueError(f'missing CSS import: {path}')
        seen.add(path)
        text = path.read_text(encoding='utf-8')
        parts.append(text)
        for raw in IMPORT_RE.findall(text):
            if EXTERNAL_RE.match(raw):
                raise ValueError(f'external CSS import: {raw}')
            clean = raw.split('?', 1)[0].split('#', 1)[0]
            target = (live / clean.lstrip('/')) if raw.startswith('/') else (path.parent / clean)
            walk(target)

    walk(entry)
    return '\n'.join(parts)
