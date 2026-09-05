#!/usr/bin/env python3
from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parents[1];LIVE=ROOT/'deploy/live';errors=[];checks=0
WORKSHOP={'index.html','en.html','start.html','en/start.html','pricing.html','en/pricing.html','family.html','en/family.html'};legacy=0
for p in sorted(LIVE.rglob('*.html')):
 if p.name=='404.html':continue
 rel=p.relative_to(LIVE).as_posix();text=p.read_text(encoding='utf-8');en=rel=='en.html' or rel.startswith('en/');expect='/en/proof' if en else '/proof'
 if rel in WORKSHOP:
  checks+=5
  if '<header class="workshopHeader">' not in text:errors.append(f'{rel}: workshop header missing')
  if text.count('aria-label="Proof Lab"')!=1:errors.append(f'{rel}: LAB action count')
  if f'href="{expect}"' not in text:errors.append(f'{rel}: proof route missing')
  if text.count('data-lab-command-open')!=1:errors.append(f'{rel}: command opener count')
  if text.count('aria-keyshortcuts="Control+K Meta+K"')!=1:errors.append(f'{rel}: shortcut count')
 else:
  legacy+=1;m=re.search(r'<header class="nav">(.*?)</header>',text,re.S);checks+=1
  if not m:errors.append(f'{rel}: legacy nav missing');continue
  h=m.group(1);checks+=2
  if h.count('aria-label="Proof Lab">LAB</a>')!=1:errors.append(f'{rel}: legacy LAB count')
  if h.count(f'href="{expect}"')<1:errors.append(f'{rel}: legacy proof href')
shell=(ROOT/'components/workshop/WorkshopShell.tsx').read_text(encoding='utf-8')
for marker in ['aria-label="Proof Lab">LAB','<LabCommand locale={locale} />']:
 checks+=1
 if marker not in shell:errors.append(f'WorkshopShell missing {marker}')
print(f'lab_discoverability_checks={checks} workshop_pages={len(WORKSHOP)} legacy_pages={legacy}')
if errors:
 for e in errors:print('FAIL:',e)
 sys.exit(1)
print('LAB_DISCOVERABILITY_PASS')
