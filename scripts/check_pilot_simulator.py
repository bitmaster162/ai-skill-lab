#!/usr/bin/env python3
from pathlib import Path
import sys, html
ROOT=Path(__file__).resolve().parents[1]
errors=[];checks=0
surfaces=[
 ('components/PilotSimulator.tsx','source shared'),
 ('app/business/page.tsx','source RU'),('app/en/business/page.tsx','source EN'),
 ('deploy/live/business.html','static RU'),('deploy/live/en/business.html','static EN')]
markers=['AI Pilot Simulator','knowledge','documents','routing','decision']
for rel,label in surfaces:
 text=html.unescape((ROOT/rel).read_text(encoding='utf-8'))
 for marker in markers:
  if rel.startswith('app/') and marker!='AI Pilot Simulator': continue
  if rel=='components/PilotSimulator.tsx' and marker=='AI Pilot Simulator': continue
  checks+=1
  if marker.lower() not in text.lower():errors.append(f'{label}: missing {marker!r}')
for rel in ['components/PilotSimulator.tsx','deploy/live/business.html','deploy/live/en/business.html']:
 text=html.unescape((ROOT/rel).read_text(encoding='utf-8'))
 for marker in ['SOURCE-BOUND','REVIEWABLE','MEASURABLE','HUMAN-OWNED','Candidate scope','AI role','Human checkpoint','Success signal','Stop condition','Pilot artifact']:
  checks+=1
  if marker not in text:errors.append(f'{rel}: missing {marker!r}')
for rel in ['deploy/live/business.html','deploy/live/en/business.html']:
 text=(ROOT/rel).read_text(encoding='utf-8')
 checks+=1
 if text.count('data-pilot-key=')!=4:errors.append(f'{rel}: expected 4 simulator buttons')
 checks+=1
 if 'data-pilot-simulator' not in text:errors.append(f'{rel}: simulator root missing')
 checks+=1
 if '<noscript>' not in text:errors.append(f'{rel}: no-JS fallback missing')
corpus='\n'.join((ROOT/r).read_text(encoding='utf-8') for r,_ in surfaces)
for bad in ['guaranteed ROI','гарантированный ROI','replace the team','заменить команду','autonomous authority to act without','автономное право действовать без']:
 checks+=1
 if bad.lower() in corpus.lower():errors.append(f'forbidden pilot claim {bad!r}')
if errors:
 print(f'pilot_simulator_checks={checks}');[print('FAIL:',e) for e in errors];sys.exit(1)
print(f'pilot_simulator_checks={checks} surfaces=5 scenarios=4')
print('PILOT_SIMULATOR_PARITY_PASS')
