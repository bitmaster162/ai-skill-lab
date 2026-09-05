#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]/'deploy'/'live'
files=[ROOT/'start.html',ROOT/'en'/'start.html',ROOT/'matcher.html',ROOT/'en'/'matcher.html']
forbidden=['fetch(', 'XMLHttpRequest', 'localStorage', 'sessionStorage', 'document.cookie', 'sendBeacon(', 'WebSocket(']
errors=[]; checks=0
brief= (ROOT/'start-brief.js').read_text(encoding='utf-8')
for p in files:
 t=p.read_text(encoding='utf-8')
 for token in forbidden:
  checks+=1
  if token in t:errors.append(f'{p.relative_to(ROOT)}: forbidden client primitive {token}')
 checks+=1
 if '<form' in t.lower():errors.append(f'{p.relative_to(ROOT)}: unexpected form')
 if p.name=='start.html':
  checks+=5
  if t.count('briefCopy')!=5:errors.append(f'{p.relative_to(ROOT)}: copy count')
  if t.count('briefSendLink')!=5:errors.append(f'{p.relative_to(ROOT)}: send count')
  if 'briefTelegramLink' in t:errors.append(f'{p.relative_to(ROOT)}: stale hook')
  if 'id="business-brief"' not in t:errors.append(f'{p.relative_to(ROOT)}: business anchor')
  if '<script src="/start-brief.js"></script>' not in t:errors.append(f'{p.relative_to(ROOT)}: helper missing')
for token in forbidden:
 checks+=1
 if token in brief:errors.append(f'start-brief.js: forbidden {token}')
for marker in ['navigator.clipboard.writeText','document.querySelectorAll(".briefSendLink")','document.querySelectorAll(".briefCopy")']:
 checks+=1
 if marker not in brief:errors.append(f'start-brief.js missing {marker}')
print(f'client_privacy_checks={checks}')
if errors:
 for e in errors:print('FAIL:',e)
 sys.exit(1)
print('CLIENT_PRIVACY_PASS')
