#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
files=['app/page.tsx','app/en/page.tsx','deploy/live/index.html','deploy/live/en.html']
required=['AI Capability Matrix','RESEARCH','BUILD','AUTOMATE','TEACH','INPUT','AI LAYER','HUMAN GATE','SHIP']
errors=[];checks=0
for rel in files:
 text=(ROOT/rel).read_text(encoding='utf-8')
 for marker in required:
  checks+=1
  if marker not in text:errors.append(f'{rel}: missing {marker!r}')
 # Four capability items, each must expose the four-stage anatomy.
 for marker in ['<h3>RESEARCH</h3>','<h3>BUILD</h3>','<h3>AUTOMATE</h3>','<h3>TEACH</h3>']:
  if rel.startswith('deploy/'):
   checks+=1
   if marker not in text:errors.append(f'{rel}: missing capability {marker}')
for bad in ['AI replaces the human','AI заменяет человека','fully autonomous by default','полностью автономно по умолчанию']:
 checks+=1
 corpus='\n'.join((ROOT/f).read_text(encoding='utf-8') for f in files)
 if bad.lower() in corpus.lower():errors.append(f'forbidden capability claim {bad!r}')
if errors:
 print(f'capability_matrix_checks={checks}');[print('FAIL:',x) for x in errors];sys.exit(1)
print(f'capability_matrix_checks={checks} surfaces=4 capabilities=4')
print('CAPABILITY_MATRIX_PARITY_PASS')
