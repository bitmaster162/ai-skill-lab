#!/usr/bin/env python3
from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parents[1]
errors=[];checks=0
surfaces=[('app/studio/page.tsx',False),('app/en/studio/page.tsx',True),('deploy/live/studio.html',False),('deploy/live/en/studio.html',True)]
common=['AI STUDIO / BUILD WITH US','CUSTOM SCOPE','AI PRODUCT / WEBSITE','RESEARCH / DECISION','AUTOMATION / AGENT','TEAM ENABLEMENT','DIAGNOSE','SCOPE','BUILD','VERIFY','SHIP','TRANSFER','Ship / Revise / Stop','/build']
for rel,en in surfaces:
    t=(ROOT/rel).read_text(encoding='utf-8')
    for marker in common:
        checks+=1
        if marker.lower() not in t.lower(): errors.append(f'{rel}: missing {marker}')
    checks+=1
    if re.search(r'\$\s?[0-9]',t): errors.append(f'{rel}: AI Studio must remain custom-scope, found hard-coded price')
    expect='/en/start' if en else '/start'; checks+=1
    if expect not in t: errors.append(f'{rel}: missing Start route {expect}')
    # Required claims discipline: negatives must be explicit, not implied.
    neg = ['guaranteed ROI','autonomous critical business decision'] if en else ['гарантированного ROI','автономного решения критичных бизнес-вопросов']
    for m in neg:
        checks+=1
        if m.lower() not in t.lower(): errors.append(f'{rel}: missing claims boundary {m}')
# Discoverability
for rel,markers in {
 'app/page.tsx':['/studio','Собрать с нами'],
 'app/en/page.tsx':['/en/studio','Build with us'],
 'deploy/live/index.html':['/studio','Собрать с нами'],
 'deploy/live/en.html':['/en/studio','Build with us'],
 'components/LabCommand.tsx':['AI Studio','/studio','/en/studio','BUILD WITH US'],
 'deploy/live/lab-command.js':['AI Studio',"b+'/studio'",'BUILD WITH US'],
}.items():
    t=(ROOT/rel).read_text(encoding='utf-8')
    for m in markers:
        checks+=1
        if m not in t: errors.append(f'{rel}: missing discoverability marker {m}')
print(f'studio_offer_checks={checks} surfaces={len(surfaces)}')
if errors:
    for e in errors: print('FAIL:',e)
    sys.exit(1)
print('AI_STUDIO_OFFER_PASS')
