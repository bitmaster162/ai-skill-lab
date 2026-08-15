#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];errors=[];checks=0
component=(ROOT/'components/SkillGraph.tsx').read_text(encoding='utf-8')
for marker in ['adult','kids','teens','business','INDEPENDENT','EXPLAINABLE','PORTFOLIO-READY','GOVERNED','data-skill-graph','data-skill-key']:
 checks+=1
 if marker not in component:errors.append(f'SkillGraph.tsx: missing {marker}')
for rel,en in [('app/curriculum/page.tsx',False),('app/en/curriculum/page.tsx',True)]:
 t=(ROOT/rel).read_text(encoding='utf-8')
 for marker in ['AI Skill Graph','SkillGraph','THINK','BUILD','VERIFY','SHIP']:
  checks+=1
  if marker.lower() not in t.lower():errors.append(f'{rel}: missing {marker}')
 expected='<SkillGraph locale="en"/>' if en else '<SkillGraph locale="ru"/>'
 checks+=1
 if expected not in t:errors.append(f'{rel}: locale mount missing')
for rel in ['deploy/live/curriculum.html','deploy/live/en/curriculum.html']:
 t=(ROOT/rel).read_text(encoding='utf-8')
 for marker in ['AI SKILL GRAPH','id="skill-graph"','data-skill-graph','data-skill-key="adult"','data-skill-key="kids"','data-skill-key="teens"','data-skill-key="business"','id="skill-signal"','id="skill-think"','id="skill-build"','id="skill-verify"','id="skill-ship"']:
  checks+=1
  if marker not in t:errors.append(f'{rel}: missing {marker}')
 for signal in ['INDEPENDENT','EXPLAINABLE','PORTFOLIO-READY','GOVERNED']:
  checks+=1
  if signal not in t:errors.append(f'{rel}: missing {signal}')
 for forbidden in ['fetch(','XMLHttpRequest','localStorage','sessionStorage','document.cookie','sendBeacon(','WebSocket(']:
  checks+=1
  if forbidden in t:errors.append(f'{rel}: forbidden primitive {forbidden}')
print(f'skill_graph_checks={checks} surfaces=5')
if errors:
 for e in errors:print('FAIL:',e)
 sys.exit(1)
print('SKILL_GRAPH_PARITY_PASS')
