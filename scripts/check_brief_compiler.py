#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
errors=[];checks=0
component=(ROOT/'components/BriefCompiler.tsx').read_text(encoding='utf-8')
for marker in ['data-brief-compiler','goal','context','output','verify','Research','Build','Automate','Learn','Solo','Team','Business','Family','Brief','Prototype','Workflow','Project','Sources','Human QA','Tests','Explain','navigator.clipboard.writeText(brief)','setCopyState("failed")','HUMAN GATE:']:
    checks+=1
    if marker not in component:errors.append(f'BriefCompiler.tsx: missing {marker}')
for rel,en in [('app/proof/page.tsx',False),('app/en/proof/page.tsx',True)]:
    t=(ROOT/rel).read_text(encoding='utf-8')
    for marker in ['BriefCompiler','id="brief-compiler"', '<BriefCompiler locale="en"/>' if en else '<BriefCompiler locale="ru"/>']:
        checks+=1
        if marker not in t:errors.append(f'{rel}: missing {marker}')
for rel,en in [('deploy/live/proof.html',False),('deploy/live/en/proof.html',True)]:
    t=(ROOT/rel).read_text(encoding='utf-8')
    for marker in ['Brief Compiler','id="brief-compiler"','data-brief-compiler','data-brief-group="goal"','data-brief-group="context"','data-brief-group="output"','data-brief-group="verify"','id="brief-copy"','id="brief-copy-status"','navigator.clipboard.writeText','HUMAN GATE:']:
        checks+=1
        if marker not in t:errors.append(f'{rel}: missing {marker}')
    for marker in ['Research','Build','Automate','Learn','Solo','Team','Business','Family','Brief','Prototype','Workflow','Project','Sources','Human QA','Tests','Explain']:
        checks+=1
        if marker not in t:errors.append(f'{rel}: option missing {marker}')
    for forbidden in ['fetch(','XMLHttpRequest','localStorage','sessionStorage','document.cookie','sendBeacon(','WebSocket(']:
        checks+=1
        if forbidden in t:errors.append(f'{rel}: forbidden primitive {forbidden}')
print(f'brief_compiler_checks={checks} surfaces=5')
if errors:
    for e in errors:print('FAIL:',e)
    sys.exit(1)
print('BRIEF_COMPILER_PARITY_PASS')
