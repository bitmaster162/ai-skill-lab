#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]/'deploy'/'live'
files=[ROOT/'start.html',ROOT/'en'/'start.html',ROOT/'matcher.html',ROOT/'en'/'matcher.html']
forbidden=['fetch(', 'XMLHttpRequest', 'localStorage', 'sessionStorage', 'document.cookie', 'sendBeacon(', 'WebSocket(']
errors=[]; checks=0
for p in files:
    t=p.read_text(encoding='utf-8')
    for token in forbidden:
        checks+=1
        if token in t: errors.append(f'{p.relative_to(ROOT)}: forbidden client persistence/network primitive {token}')
    checks+=1
    if '<form' in t.lower(): errors.append(f'{p.relative_to(ROOT)}: unexpected form')
    if p.name=='start.html':
        checks+=2
        if t.count('class="btn ghost briefCopy"') != 4: errors.append(f'{p.relative_to(ROOT)}: expected 4 copy buttons')
        if 'navigator.clipboard.writeText' not in t: errors.append(f'{p.relative_to(ROOT)}: clipboard helper missing')
print(f'client_privacy_checks={checks}')
if errors:
    for e in errors: print('FAIL:',e)
    sys.exit(1)
print('CLIENT_PRIVACY_PASS')
