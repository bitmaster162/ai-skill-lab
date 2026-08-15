#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]; checks=0
surfaces=[
 ('app/page.tsx','/proof','/start',['01 / Site as proof','02 / CHOOSE A TRACK','03 / AI Capability Matrix','04 / ENGAGE']),
 ('app/en/page.tsx','/en/proof','/en/start',['01 / Site as proof','02 / CHOOSE A TRACK','03 / AI Capability Matrix','04 / ENGAGE']),
 ('deploy/live/index.html','/proof','/start',['01 / Site as proof','02 / CHOOSE A TRACK','03 / AI Capability Matrix','04 / ENGAGE']),
 ('deploy/live/en.html','/en/proof','/en/start',['01 / Site as proof','02 / CHOOSE A TRACK','03 / AI Capability Matrix','04 / ENGAGE']),
]
for rel,proof,start,chapters in surfaces:
 t=(ROOT/rel).read_text(encoding='utf-8')
 for marker in chapters:
  checks+=1
  if marker not in t: errors.append(f'{rel}: missing {marker!r}')
 checks+=1
 if proof not in t: errors.append(f'{rel}: proof CTA missing {proof}')
 checks+=1
 if start not in t: errors.append(f'{rel}: start CTA missing {start}')
for rel in ['deploy/live/index.html','deploy/live/en.html']:
 t=(ROOT/rel).read_text(encoding='utf-8')
 for marker in ['AI SKILL ENGINE','LIVE SCENE']:
  checks+=1
  if marker not in t: errors.append(f'{rel}: missing {marker!r}')
for rel in ['components/HeroEngine.tsx','deploy/live/index.html','deploy/live/en.html']:
 t=(ROOT/rel).read_text(encoding='utf-8')
 for marker in ['engineWorkbench','engineTrack','engineReceipt','engine-focus','engine-output']:
  checks+=1
  if marker not in t: errors.append(f'{rel}: product scene missing {marker}')
if errors:
 print(f'attention_hierarchy_checks={checks}')
 for e in errors: print('FAIL:',e)
 sys.exit(1)
print(f'attention_hierarchy_checks={checks} surfaces=4 scene_surfaces=3')
print('ATTENTION_HIERARCHY_PASS')
