#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];errors=[];checks=0
component=(ROOT/'components/SystemChallenge.tsx').read_text(encoding='utf-8')
for marker in ['research','product','automation','learning','SOURCE-BOUND','SHIPPABLE','REPEATABLE','TRANSFERABLE','data-system-challenge','data-challenge-key']:
    checks+=1
    if marker not in component:errors.append(f'SystemChallenge.tsx: missing {marker}')
for rel,en in [('app/challenge/page.tsx',False),('app/en/challenge/page.tsx',True)]:
    t=(ROOT/rel).read_text(encoding='utf-8')
    for marker in ['AI SYSTEM CHALLENGE','SystemChallenge','id="challenge"','Brief Compiler','stop condition' if en else 'stop condition']:
        checks+=1
        if marker.lower() not in t.lower():errors.append(f'{rel}: missing {marker}')
    checks+=1
    expected='<SystemChallenge locale="en"/>' if en else '<SystemChallenge locale="ru"/>'
    if expected not in t:errors.append(f'{rel}: locale mount missing')
for rel,en in [('deploy/live/challenge.html',False),('deploy/live/en/challenge.html',True)]:
    t=(ROOT/rel).read_text(encoding='utf-8')
    for marker in ['AI SYSTEM CHALLENGE','data-system-challenge','data-challenge-key="research"','data-challenge-key="product"','data-challenge-key="automation"','data-challenge-key="learning"','id="challenge-weak"','id="challenge-title"','id="challenge-signal"','VAGUE → SYSTEMIZED']:
        checks+=1
        if marker not in t:errors.append(f'{rel}: missing {marker}')
    for signal in ['SOURCE-BOUND','SHIPPABLE','REPEATABLE','TRANSFERABLE']:
        checks+=1
        if signal not in t:errors.append(f'{rel}: signal missing {signal}')
    for forbidden in ['fetch(','XMLHttpRequest','localStorage','sessionStorage','document.cookie','sendBeacon(','WebSocket(']:
        checks+=1
        if forbidden in t:errors.append(f'{rel}: forbidden primitive {forbidden}')
    checks+=3
    route='/en/challenge' if en else '/challenge'
    pair='/challenge' if en else '/en/challenge'
    if f'<link rel="canonical" href="https://ai-skill-lab.vercel.app{route}">' not in t:errors.append(f'{rel}: canonical mismatch')
    if f'href="https://ai-skill-lab.vercel.app{pair}"' not in t:errors.append(f'{rel}: hreflang pair missing')
    if 'aria-current="page"' in t:errors.append(f'{rel}: inherited active nav marker')
for rel in ['app/sitemap.ts','deploy/live/sitemap.xml']:
    t=(ROOT/rel).read_text(encoding='utf-8')
    for route in ['/challenge','/en/challenge']:
        checks+=1
        if route not in t:errors.append(f'{rel}: missing {route}')
print(f'system_challenge_checks={checks} surfaces=5')
if errors:
    for e in errors:print('FAIL:',e)
    sys.exit(1)
print('SYSTEM_CHALLENGE_PARITY_PASS')
