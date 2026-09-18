#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];LIVE=ROOT/'deploy/live';errors=[];checks=0
WORKSHOP={'business.html','en.html','en/business.html','en/family.html','en/faq.html','en/kids.html','en/personal.html','en/pricing.html','en/start.html','en/teens.html','family.html','faq.html','index.html','kids.html','personal.html','pricing.html','start.html','teens.html','parents.html','curriculum.html','phuket.html','studio.html','build.html','matcher.html','challenge.html','proof.html','projects.html','en/parents.html','en/curriculum.html','en/phuket.html','en/studio.html','en/build.html','en/matcher.html','en/challenge.html','en/proof.html','en/projects.html','about.html','method.html','safety.html','privacy.html','terms.html','en/about.html','en/method.html','en/safety.html','en/privacy.html','en/terms.html'}
pages=[p for p in sorted(LIVE.rglob('*.html')) if p.name!='404.html'];legacy=0
for p in pages:
 rel=p.relative_to(LIVE).as_posix();t=p.read_text(encoding='utf-8')
 if rel in WORKSHOP:
  for token,count in [('id="lab-command"',1),('src="/lab-command.js"',1),('aria-keyshortcuts="Control+K Meta+K"',1),('data-lab-command-open',1),('<span data-kbd-mod>Ctrl</span> K',1)]:
   checks+=1
   if t.count(token)!=count:errors.append(f'{rel}: {token} count={t.count(token)} expected={count}')
  checks+=1
  if '>⌘K</button>' in t:errors.append(f'{rel}: raw Apple-only shortcut label remains')
 else:
  legacy+=1
src=(ROOT/'components/LabCommand.tsx').read_text(encoding='utf-8')
source_css=(ROOT/'components/workshop/WorkshopShell.module.css').read_text(encoding='utf-8')
static_css=(LIVE/'workshop.css').read_text(encoding='utf-8')
for marker in ['showModal()','event.metaKey || event.ctrlKey','aria-keyshortcuts="Control+K Meta+K"','<span data-kbd-mod="">Ctrl</span> K','navigator.platform || navigator.userAgent','Project Studio','Pilot Simulator','Program Matcher','AI Challenge','Build Log','AI Studio']:
 checks+=1
 if marker not in src:errors.append(f'LabCommand.tsx missing {marker}')
for name,text,marker in [('source CSS',source_css,':global(.labCommandTrigger){min-width:64px'),('static CSS',static_css,'[data-lab-command-open],.labCommandTrigger{min-width:64px')]:
 checks+=1
 if marker not in text:errors.append(f'{name} missing stable shortcut width')
header=(ROOT/'components/Header.tsx').read_text(encoding='utf-8');shell=(ROOT/'components/workshop/WorkshopShell.tsx').read_text(encoding='utf-8')
for rel,text,marker in [('Header.tsx',header,'<LabCommand locale={locale} />'),('WorkshopShell.tsx',shell,'<LabCommand locale={locale} />')]:
 checks+=1
 if marker not in text:errors.append(f'{rel}: command mount missing')
js=(LIVE/'lab-command.js').read_text(encoding='utf-8')
for marker in ['document.documentElement.lang','d.innerHTML','data-lab-command-close','data-kbd-mod','navigator.platform||navigator.userAgent','/proof','/projects','/business#pilot-simulator','/matcher','/challenge','/build','/studio','/start']:
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
