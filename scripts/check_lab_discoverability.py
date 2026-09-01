#!/usr/bin/env python3
from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parents[1]; LIVE=ROOT/'deploy/live'; errors=[];checks=0
R77_HOMES={'index.html':'/proof','en.html':'/en/proof'}
src=(ROOT/'components/Header.tsx').read_text(encoding='utf-8');checks+=2
if 'href={`${base}/proof`}' not in src:errors.append('source Header missing locale-aware Proof Lab action')
if 'aria-label="Proof Lab">LAB' not in src:errors.append('source Header missing LAB label')
legacy_pages=0
for p in sorted(LIVE.rglob('*.html')):
 if p.name=='404.html':continue
 rel=p.relative_to(LIVE).as_posix();text=p.read_text(encoding='utf-8')
 if rel in R77_HOMES:
  expect=R77_HOMES[rel];checks+=3
  if '<header class="header">' not in text:errors.append(f'{rel}: R77 commercial header missing')
  if f'href="{expect}"' not in text:errors.append(f'{rel}: direct Proof route missing')
  if 'aria-label="Proof Lab">LAB</a>' in text:errors.append(f'{rel}: legacy LAB header action must not return')
  continue
 legacy_pages+=1
 en=rel.startswith('en/');expect='/en/proof' if en else '/proof'
 m=re.search(r'<header class="nav">(.*?)</header>',text,re.S);checks+=1
 if not m:errors.append(f'{rel}: nav missing');continue
 h=m.group(1);checks+=3
 if h.count('aria-label="Proof Lab">LAB</a>')!=1:errors.append(f'{rel}: LAB action count mismatch')
 if h.count(f'href="{expect}"')<1:errors.append(f'{rel}: proof href missing')
 if h.count('class="langSwitch"')<2:errors.append(f'{rel}: expected LAB + language switches')
if errors:
 print(f'lab_discoverability_checks={checks} legacy_pages={legacy_pages} r77_homes={len(R77_HOMES)}');[print('FAIL:',e) for e in errors];sys.exit(1)
print(f'lab_discoverability_checks={checks} legacy_pages={legacy_pages} r77_homes={len(R77_HOMES)}')
print('LAB_DISCOVERABILITY_PASS')
