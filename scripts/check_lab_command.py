#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/'deploy'/'live'
errors=[];checks=0
pages=[p for p in sorted(LIVE.rglob('*.html')) if p.name!='404.html']
for p in pages:
    rel=p.relative_to(LIVE).as_posix();t=p.read_text(encoding='utf-8')
    for token,count in [('id="lab-command"',1),('src="/lab-command.js"',1),('aria-keyshortcuts="Control+K Meta+K"',1)]:
        checks+=1
        if t.count(token)!=count:errors.append(f'{rel}: {token} count={t.count(token)} expected={count}')
    checks+=1
    if t.count('data-lab-command-open')<1:errors.append(f'{rel}: missing Lab Command opener')
    checks+=1
    if '<dialog class="labDialog" id="lab-command"' not in t:errors.append(f'{rel}: shared dialog mount missing')
    checks+=1
    if 'data-lab-command-close' in t:errors.append(f'{rel}: dialog body must come from shared runtime, not repeated HTML')

src=(ROOT/'components'/'LabCommand.tsx').read_text(encoding='utf-8')
header=(ROOT/'components'/'Header.tsx').read_text(encoding='utf-8')
for marker in ['showModal()','event.metaKey || event.ctrlKey','aria-keyshortcuts="Control+K Meta+K"','Project Studio','Pilot Simulator','Program Matcher','AI Challenge','Build Log']:
    checks+=1
    if marker not in src:errors.append(f'LabCommand.tsx: missing {marker}')
checks+=1
if '<LabCommand locale={locale} />' not in header:errors.append('Header.tsx: LabCommand not mounted')
js=(LIVE/'lab-command.js').read_text(encoding='utf-8')
for marker in ['document.documentElement.lang','d.innerHTML','data-lab-command-close','/proof','/projects','/business#pilot-simulator','/matcher','/challenge','/build','/start']:
    checks+=1
    if marker not in js:errors.append(f'lab-command.js: shared runtime missing {marker}')
for forbidden in ['fetch(','XMLHttpRequest','localStorage','sessionStorage','document.cookie','sendBeacon(','WebSocket(']:
    checks+=1
    if forbidden in js:errors.append(f'lab-command.js: forbidden primitive {forbidden}')

print(f'lab_command_checks={checks} pages={len(pages)}')
if errors:
    for e in errors:print('FAIL:',e)
    sys.exit(1)
print('LAB_COMMAND_PARITY_PASS')
