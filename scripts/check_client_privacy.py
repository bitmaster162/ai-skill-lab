#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]/'deploy'/'live'
starts=[ROOT/'start.html',ROOT/'en'/'start.html']; matchers=[ROOT/'matcher.html',ROOT/'en'/'matcher.html']
errors=[]; checks=0
for p in [*starts,*matchers]:
 t=p.read_text(encoding='utf-8')
 for token in ['fetch(', 'XMLHttpRequest', 'localStorage', 'sessionStorage', 'document.cookie', 'sendBeacon(', 'WebSocket(']:
  checks+=1
  if token in t: errors.append(f'{p.relative_to(ROOT)}: inline/network primitive {token}')
 if p in starts:
  checks+=7
  if t.lower().count('<form')!=1: errors.append(f'{p.relative_to(ROOT)}: expected one application form')
  if 'id="application-form"' not in t: errors.append(f'{p.relative_to(ROOT)}: application form id')
  if t.count('briefCopy')!=5 or t.count('briefSendLink')!=5: errors.append(f'{p.relative_to(ROOT)}: brief fallback drift')
  if 'briefTelegramLink' in t: errors.append(f'{p.relative_to(ROOT)}: stale hook')
  if 'id="business-brief"' not in t: errors.append(f'{p.relative_to(ROOT)}: business anchor')
  if '<script src="/start-brief.js"></script>' not in t: errors.append(f'{p.relative_to(ROOT)}: helper missing')
  if 'action=' in t.lower(): errors.append(f'{p.relative_to(ROOT)}: native form action forbidden')
brief=(ROOT/'start-brief.js').read_text(encoding='utf-8')
checks+=1
if brief.count('fetch("/api/lead"')!=1: errors.append('start-brief.js must contain exactly one same-origin lead fetch')
for token in ['XMLHttpRequest','localStorage','sessionStorage','document.cookie','sendBeacon(','WebSocket(','https://ai-skill-lab-ingress']:
 checks+=1
 if token in brief: errors.append(f'start-brief.js forbidden {token}')
for marker in ['navigator.clipboard.writeText','document.querySelectorAll(".briefSendLink")','document.querySelectorAll(".briefCopy")','new FormData(form)','"Content-Type":"application/json"','data-adult-confirmation']:
 checks+=1
 if marker not in brief: errors.append(f'start-brief.js missing {marker}')
print(f'client_privacy_checks={checks}')
if errors:
 [print('FAIL:',e) for e in errors]; sys.exit(1)
print('CLIENT_PRIVACY_PASS')
