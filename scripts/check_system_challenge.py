#!/usr/bin/env python3
from pathlib import Path
from source_paths import source_path
import sys,json
from public_origin import PUBLIC_ORIGIN
ROOT=Path(__file__).resolve().parents[1];errors=[];checks=0
E32=json.loads((ROOT/'deploy/live/_release.json').read_text(encoding='utf8')).get('release_id') in {'E3_2_RU_GLOSSARY_R1','E3_4_AI_SAFETY_AUDIENCE_R1','E3_5_HEADING_STRUCTURE_R1','E3_6_WORKSHOP_HERO_PANEL_R1'}
component=(ROOT/'components/SystemChallenge.tsx').read_text(encoding='utf-8')
for marker in ['research','product','automation','learning','SOURCE-BOUND','SHIPPABLE','REPEATABLE','TRANSFERABLE','data-system-challenge','data-challenge-key']:
    checks+=1
    if marker not in component:errors.append(f'SystemChallenge.tsx: missing {marker}')
for rel,en in [('app/challenge/page.tsx',False),('app/en/challenge/page.tsx',True)]:
    t=source_path(ROOT, rel).read_text(encoding='utf-8')
    for marker in [('ЗАДАНИЕ ПО ИИ' if E32 and not en else 'AI SYSTEM CHALLENGE'),'SystemChallenge','id="challenge"',('Составление задачи' if E32 and not en else 'Brief Compiler'),'stop condition']:
        checks+=1
        if marker.lower() not in t.lower():errors.append(f'{rel}: missing {marker}')
    checks+=1
    expected='<SystemChallenge locale="en"/>' if en else '<SystemChallenge locale="ru"/>'
    if expected not in t:errors.append(f'{rel}: locale mount missing')
for rel,en in [('deploy/live/challenge.html',False),('deploy/live/en/challenge.html',True)]:
    t=source_path(ROOT, rel).read_text(encoding='utf-8')
    for marker in [('ЗАДАНИЕ ПО ИИ' if E32 and not en else 'AI SYSTEM CHALLENGE'),'data-system-challenge','data-challenge-key="research"','data-challenge-key="product"','data-challenge-key="automation"','data-challenge-key="learning"','id="challenge-weak"','id="challenge-title"','id="challenge-signal"',('РАЗМЫТО → СИСТЕМА' if E32 and not en else 'VAGUE → SYSTEMIZED')]:
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
    if f'<link rel="canonical" href="{PUBLIC_ORIGIN}{route}">' not in t:errors.append(f'{rel}: canonical mismatch')
    if f'href="{PUBLIC_ORIGIN}{pair}"' not in t:errors.append(f'{rel}: hreflang pair missing')
    if 'aria-current="page"' in t:errors.append(f'{rel}: inherited active nav marker')
for rel in ['app/sitemap.ts','deploy/live/sitemap.xml']:
    t=source_path(ROOT, rel).read_text(encoding='utf-8')
    for route in ['/challenge','/en/challenge']:
        checks+=1
        if route not in t:errors.append(f'{rel}: missing {route}')
print(f'system_challenge_checks={checks} surfaces=5')
if errors:
    for e in errors:print('FAIL:',e)
    sys.exit(1)
print('SYSTEM_CHALLENGE_PARITY_PASS')
