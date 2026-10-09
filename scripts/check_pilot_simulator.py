#!/usr/bin/env python3
from pathlib import Path
import json
import sys, html
ROOT=Path(__file__).resolve().parents[1]
E32 = json.loads((ROOT / "deploy/live/_release.json").read_text(encoding="utf-8")).get("release_id")  in {'E3_2_RU_GLOSSARY_R1','E3_4_AI_SAFETY_AUDIENCE_R1','E3_5_HEADING_STRUCTURE_R1'}
errors=[];checks=0
surfaces=[
 ('components/PilotSimulator.tsx','source shared'),
 ('components/workshop/WorkshopBusiness.tsx','source RU'),('components/workshop/WorkshopBusiness.tsx','source EN'),
 ('deploy/live/business.html','static RU'),('deploy/live/en/business.html','static EN')]
markers=['AI Pilot Simulator','knowledge','documents','routing','decision']
for rel,label in surfaces:
 text=html.unescape((ROOT/rel).read_text(encoding='utf-8'))
 for marker in markers:
  if label in ('source RU','source EN') and marker!='AI Pilot Simulator': continue
  if rel=='components/PilotSimulator.tsx' and marker=='AI Pilot Simulator': continue
  checks+=1
  required = "Симулятор пилота" if E32 and label == "static RU" and marker == "AI Pilot Simulator" else marker
  if required.lower() not in text.lower():errors.append(f'{label}: missing {required!r}')
E32_PILOT = {
 "Candidate scope":"Возможный объём работ",
 "AI role":"Роль ИИ",
 "Human checkpoint":"Проверка человеком",
 "Success signal":"Критерий успеха",
 "Stop condition":"Условие остановки",
 "Pilot artifact":"Результат пилота",
}
for rel in ['components/PilotSimulator.tsx','deploy/live/business.html','deploy/live/en/business.html']:
 text=html.unescape((ROOT/rel).read_text(encoding='utf-8'))
 for marker in ['SOURCE-BOUND','REVIEWABLE','MEASURABLE','HUMAN-OWNED','Candidate scope','AI role','Human checkpoint','Success signal','Stop condition','Pilot artifact']:
  checks+=1
  required = E32_PILOT.get(marker,marker) if E32 and rel == 'deploy/live/business.html' else marker
  if required not in text:errors.append(f'{rel}: missing {required!r}')
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
