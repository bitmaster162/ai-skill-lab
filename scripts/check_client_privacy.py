#!/usr/bin/env python3
from guide_route_admission import admitted_route_count, require_public_html, require_route_set, require_canonical_urls
from pathlib import Path
import sys
REPO=Path(__file__).resolve().parents[1]
ROOT=REPO/'deploy'/'live'
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
matcher_v2=(ROOT/'matcher-v2.js').read_text(encoding='utf-8')
checks+=3
if brief.count('fetch("/api/lead"')!=1: errors.append('start-brief.js must contain exactly one same-origin lead fetch')
if matcher_v2.count('fetch("/api/route"')!=1: errors.append('matcher-v2.js must contain exactly one same-origin route fetch')
if matcher_v2.count('fetch("/api/lead"')!=1: errors.append('matcher-v2.js must contain exactly one consent-gated lead fetch')
for token in ['XMLHttpRequest','localStorage','sessionStorage','document.cookie','sendBeacon(','WebSocket(','https://ai-skill-lab-ingress']:
 checks+=2
 if token in brief: errors.append(f'start-brief.js forbidden {token}')
 if token in matcher_v2: errors.append(f'matcher-v2.js forbidden {token}')
for marker in ['navigator.clipboard.writeText','document.querySelectorAll(".briefSendLink")','document.querySelectorAll(".briefCopy")','new FormData(form)','"Content-Type":"application/json"','data-adult-confirmation']:
 checks+=1
 if marker not in brief: errors.append(f'start-brief.js missing {marker}')
static_css=(ROOT/'workshop.css').read_text(encoding='utf-8')
checks+=2
if '.leadForm .consentRow{grid-template-columns:24px 1fr;min-height:24px;padding:3px 0;' not in static_css:
 errors.append('workshop.css consent target must be >=24px')
if '.leadForm .consentRow input{width:18px;min-height:18px;height:18px;' not in static_css:
 errors.append('workshop.css visual checkbox size drift')
source_css=(REPO/'app/globals.css').read_text(encoding='utf-8')
checks+=1
if 'grid-template-columns: 24px 1fr; min-height: 24px; padding: 3px 0;' not in source_css:
 errors.append('source consent label target must be >=24px')
proofs=[
 (ROOT/'proof.html',"Публичный сайт использует Vercel Web Analytics для обезличенной статистики посещений; cookies и рекламные trackers не используются. Формы есть на /start и /matcher: matcher вызывает /api/route только по кнопке, а brief отправляет в /api/lead только по согласию."),
 (ROOT/'en'/'proof.html',"The public site uses Vercel Web Analytics for anonymized visit statistics; it uses no cookies or advertising trackers. Forms exist on /start and /matcher: matcher calls /api/route only on button press, and sends its brief to /api/lead only with consent."),
]
analytics_tag='<script defer src="/_vercel/insights/script.js"></script>'
public_html=[p for p in ROOT.rglob('*.html') if p.name!='404.html']
checks+=len(public_html)+1
require_public_html(ROOT)
if len(public_html)!=admitted_route_count(): errors.append(f'analytics route count {len(public_html)} != {admitted_route_count()}')
for p in public_html:
 t=p.read_text(encoding='utf-8')
 if t.count(analytics_tag)!=1: errors.append(f'{p.relative_to(ROOT)}: analytics script count {t.count(analytics_tag)} != 1')
for p,privacy in proofs:
 t=p.read_text(encoding='utf-8'); checks+=4
 if '<b>public_forms</b><strong>2</strong>' not in t: errors.append(f'{p.relative_to(ROOT)}: public_forms must equal 2')
 if '<b>public_forms</b><strong>0</strong>' in t or '<b>public_forms</b><strong>1</strong>' in t: errors.append(f'{p.relative_to(ROOT)}: stale public_forms count')
 if privacy not in t: errors.append(f'{p.relative_to(ROOT)}: current privacy statement missing')
 if 'first-party lead forms' in t or 'first-party lead forms' in t.lower(): errors.append(f'{p.relative_to(ROOT)}: stale no-form claim')
print(f'client_privacy_checks={checks}')
if errors:
 [print('FAIL:',e) for e in errors]; sys.exit(1)
print('CLIENT_PRIVACY_PASS')
