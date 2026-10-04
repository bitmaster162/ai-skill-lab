#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy" / "live"
CALCOM = "https://cal.com/robert-dumanyan-vlck0x/15min"

TARGETS = {
    "start.html": "Бесплатный звонок-знакомство · 15 минут",
    "en/start.html": "Free 15-minute intro call",
}

def patch_start(path: Path, label: str) -> bool:
    raw = path.read_text(encoding="utf-8")
    pattern = re.compile(
        r'<a class="workshopButton workshopButtonPrimary" '
        r'data-intro-call-channel="(?:whatsapp|calcom)" '
        r'href="[^"]+" target="_blank" rel="noopener noreferrer">'
        + re.escape(label) +
        r'</a>'
    )
    replacement = (
        '<a class="workshopButton workshopButtonPrimary" '
        'data-intro-call-channel="calcom" '
        f'href="{CALCOM}" target="_blank" rel="noopener noreferrer">'
        f'{label}</a>'
    )
    new, count = pattern.subn(replacement, raw, count=1)
    if count != 1:
        raise RuntimeError(f"{path}: primary intro anchor count={count}")
    if new != raw:
        path.write_text(new, encoding="utf-8", newline="\n")
        return True
    return False

def patch_runtime() -> bool:
    path = LIVE / "lab-command.js"
    raw = path.read_text(encoding="utf-8")
    old = 'if(channel!=="whatsapp"&&channel!=="telegram")return;'
    new = 'if(channel!=="whatsapp"&&channel!=="telegram"&&channel!=="calcom")return;'
    if new in raw:
        return False
    if raw.count(old) != 1:
        raise RuntimeError(f"lab-command.js: tracker anchor count={raw.count(old)}")
    path.write_text(raw.replace(old, new, 1), encoding="utf-8", newline="\n")
    return True

def main() -> int:
    changed = 0
    for rel, label in TARGETS.items():
        changed += int(patch_start(LIVE / rel, label))
    runtime_changed = patch_runtime()
    print(
        f"A3_CALCOM_BUILD_PASS pages=2 page_changes={changed} "
        f"runtime_changed={str(runtime_changed).lower()} url={CALCOM}"
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
