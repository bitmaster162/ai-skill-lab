#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];errors=[];checks=0
surfaces=[('app/proof/page.tsx',False),('app/en/proof/page.tsx',True),('deploy/live/proof.html',False),('deploy/live/en/proof.html',True)]
for rel,en in surfaces:
 text=(ROOT/rel).read_text(encoding='utf-8')
 for marker in ['Live demo surfaces' if rel.startswith('app/') else 'LIVE DEMO SURFACES','Workflow Lab','Brief Compiler','Project Studio','AI Pilot Simulator']:
  checks+=1
  if marker.lower() not in text.lower():errors.append(f'{rel}: missing {marker}')
 expected=['#lab','#brief-compiler','/en/projects' if en else '/projects','/en/business#pilot-simulator' if en else '/business#pilot-simulator','/en/build' if en else '/build']
 for href in expected:
  checks+=1
  if href not in text:errors.append(f'{rel}: missing {href}')
for rel in ['components/workshop/WorkshopBusiness.tsx','components/workshop/WorkshopBusiness.tsx','deploy/live/business.html','deploy/live/en/business.html']:
 text=(ROOT/rel).read_text(encoding='utf-8');checks+=1
 if 'id="pilot-simulator"' not in text:errors.append(f'{rel}: pilot simulator anchor missing')
if errors:
 print(f'lab_hub_checks={checks}');[print('FAIL:',e) for e in errors];sys.exit(1)
print(f'lab_hub_checks={checks} proof_surfaces=4')
print('LAB_HUB_PASS')
