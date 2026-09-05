#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];LIVE=ROOT/'deploy/live';errors=[];checks=0
WORKSHOP={'business.html','en.html','en/business.html','en/family.html','en/faq.html','en/kids.html','en/personal.html','en/pricing.html','en/start.html','en/teens.html','family.html','faq.html','index.html','kids.html','personal.html','pricing.html','start.html','teens.html'}
pages=[p for p in sorted(LIVE.rglob('*.html')) if p.name!='404.html'];legacy=0
for p in pages:
 rel=p.relative_to(LIVE).as_posix();t=p.read_text(encoding='utf-8')
 if rel in WORKSHOP:
  for token,count in [('id="lab-command"',1),('src="/lab-command.js"',1),('aria-keyshortcuts="Control+K Meta+K"',1),('data-lab-command-open',1)]:
   checks+=1
   if t.count(token)!=count:errors.append(f'{rel}: {token} count={t.count(token)} expected={count}')
 else:
  legacy+=1
  for token,count in [('id="lab-command"',1),('src="/lab-command.js"',1),('aria-keyshortcuts="Control+K Meta+K"',1)]:
   checks+=1
   if t.count(token)!=count:errors.append(f'{rel}: {token} count drift')
  checks+=1
  if t.count('data-lab-command-open')<1:errors.append(f'{rel}: opener missing')
src=(ROOT/'components/LabCommand.tsx').read_text(encoding='utf-8');header=(ROOT/'components/Header.tsx').read_text(encoding='utf-8');shell=(ROOT/'components/workshop/WorkshopShell.tsx').read_text(encoding='utf-8')
for marker in ['showModal()','event.metaKey || event.ctrlKey','aria-keyshortcuts="Control+K Meta+K"','Project Studio','Pilot Simulator','Program Matcher','AI Challenge','Build Log','AI Studio']:
 checks+=1
 if marker not in src:errors.append(f'LabCommand.tsx missing {marker}')
for rel,text,marker in [('Header.tsx',header,'<LabCommand locale={locale} />'),('WorkshopShell.tsx',shell,'<LabCommand locale={locale} />')]:
 checks+=1
 if marker not in text:errors.append(f'{rel}: command mount missing')
js=(LIVE/'lab-command.js').read_text(encoding='utf-8')
for marker in ['document.documentElement.lang','d.innerHTML','data-lab-command-close','/proof','/projects','/business#pilot-simulator','/matcher','/challenge','/build','/studio','/start']:
 checks+=1
 if marker not in js:errors.append(f'lab-command.js missing {marker}')
for forbidden in ['fetch(','XMLHttpRequest','localStorage','sessionStorage','document.cookie','sendBeacon(','WebSocket(']:
 checks+=1
 if forbidden in js:errors.append(f'lab-command.js forbidden {forbidden}')
print(f'lab_command_checks={checks} workshop_pages={len(WORKSHOP)} legacy_pages={legacy}')
if errors:
 for e in errors:print('FAIL:',e)
 sys.exit(1)
print('LAB_COMMAND_PARITY_PASS')
