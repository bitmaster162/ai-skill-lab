#!/usr/bin/env python3
from pathlib import Path
import json
from source_paths import source_path
import sys
ROOT=Path(__file__).resolve().parents[1];errors=[];checks=0
E32 = json.loads((ROOT / "deploy/live/_release.json").read_text(encoding="utf-8")).get("release_id")  in {'E3_2_RU_GLOSSARY_R1','E3_4_AI_SAFETY_AUDIENCE_R1'}
surfaces=[('app/proof/page.tsx',False),('app/en/proof/page.tsx',True),('deploy/live/proof.html',False),('deploy/live/en/proof.html',True)]
E32_HUB = {"Live demo surfaces":"РАБОТАЮЩИЕ ДЕМОНСТРАЦИИ",
            "LIVE DEMO SURFACES":"РАБОТАЮЩИЕ ДЕМОНСТРАЦИИ",
            "Workflow Lab":"Лаборатория рабочих процессов",
            "Brief Compiler":"Составление задачи",
            "Project Studio":"Примеры проектов",
            "AI Pilot Simulator":"Симулятор пилота"}
for rel,en in surfaces:
 text=source_path(ROOT, rel).read_text(encoding='utf-8')
 for marker in ['Live demo surfaces' if rel.startswith('app/') else 'LIVE DEMO SURFACES','Workflow Lab','Brief Compiler','Project Studio','AI Pilot Simulator']:
  checks+=1
  required = E32_HUB.get(marker,marker) if E32 and not en else marker
  if required.lower() not in text.lower():errors.append(f'{rel}: missing {required}')
 expected=['#lab','#brief-compiler','/en/projects' if en else '/projects','/en/business#pilot-simulator' if en else '/business#pilot-simulator','/en/build' if en else '/build']
 for href in expected:
  checks+=1
  if href not in text:errors.append(f'{rel}: missing {href}')
for rel in ['components/workshop/WorkshopBusiness.tsx','components/workshop/WorkshopBusiness.tsx','deploy/live/business.html','deploy/live/en/business.html']:
 text=source_path(ROOT, rel).read_text(encoding='utf-8');checks+=1
 if 'id="pilot-simulator"' not in text:errors.append(f'{rel}: pilot simulator anchor missing')
if errors:
 print(f'lab_hub_checks={checks}');[print('FAIL:',e) for e in errors];sys.exit(1)
print(f'lab_hub_checks={checks} proof_surfaces=4')
print('LAB_HUB_PASS')
