#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/'deploy'/'live'
errors=[];checks=0
pages=[p for p in sorted(LIVE.rglob('*.html')) if p.name!='404.html']
for p in pages:
    rel=p.relative_to(LIVE).as_posix();t=p.read_text(encoding='utf-8')
    en=rel=='en.html' or rel.startswith('en/')
    expected=['/en/proof','/en/projects','/en/business#pilot-simulator','/en/matcher','/en/challenge','/en/start'] if en else ['/proof','/projects','/business#pilot-simulator','/matcher','/challenge','/start']
    for token,count in [
        ('data-lab-command-open',1),('id="lab-command"',1),('data-lab-command-close',1),('src="/lab-command.js"',1),('aria-keyshortcuts="Control+K Meta+K"',1)
    ]:
        checks+=1
        if t.count(token)!=count:errors.append(f'{rel}: {token} count={t.count(token)} expected={count}')
    for href in expected:
        checks+=1
        # destination must exist in command dialog; other page links may also use it
        dialog=t.split('<dialog class="labDialog"',1)[1] if '<dialog class="labDialog"' in t else ''
        if f'href="{href}"' not in dialog:errors.append(f'{rel}: command destination missing {href}')
    checks+=1
    if 'CTRL / ⌘ + K' not in t:errors.append(f'{rel}: shortcut hint missing')

src=(ROOT/'components'/'LabCommand.tsx').read_text(encoding='utf-8')
header=(ROOT/'components'/'Header.tsx').read_text(encoding='utf-8')
for marker in ['showModal()','event.metaKey || event.ctrlKey','aria-keyshortcuts="Control+K Meta+K"','Project Studio','Pilot Simulator','Program Matcher','AI Challenge']:
    checks+=1
    if marker not in src:errors.append(f'LabCommand.tsx: missing {marker}')
checks+=1
if '<LabCommand locale={locale} />' not in header:errors.append('Header.tsx: LabCommand not mounted')
js=(LIVE/'lab-command.js').read_text(encoding='utf-8')
for forbidden in ['fetch(','XMLHttpRequest','localStorage','sessionStorage','document.cookie','sendBeacon(','WebSocket(']:
    checks+=1
    if forbidden in js:errors.append(f'lab-command.js: forbidden primitive {forbidden}')

print(f'lab_command_checks={checks} pages={len(pages)}')
if errors:
    for e in errors:print('FAIL:',e)
    sys.exit(1)
print('LAB_COMMAND_PARITY_PASS')
