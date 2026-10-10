#!/usr/bin/env python3
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
required=[('components/workshop/WorkshopBusiness.tsx', ['Ship · Revise · Stop.', 'human review', 'failure modes', 'data boundaries', 'fallback', 'Stop']), ('components/workshop/WorkshopBusiness.tsx', ['Ship · Revise · Stop.', 'human review', 'failure modes', 'data boundaries', 'fallback', 'Stop']), ('deploy/live/business.html', ['Ship · Revise · Stop.', 'human review', 'failure modes', 'data boundaries', 'fallback', 'STOP']), ('deploy/live/en/business.html', ['Ship · Revise · Stop.', 'human review', 'failure modes', 'data boundaries', 'fallback', 'STOP'])]
if json.loads((ROOT/'deploy/live/_release.json').read_text(encoding='utf8')).get('release_id') in {'E3_2_RU_GLOSSARY_R1','E3_4_AI_SAFETY_AUDIENCE_R1','E3_5_HEADING_STRUCTURE_R1','E3_6_WORKSHOP_HERO_PANEL_R1'}:
    ru=['Выпустить · Доработать · Остановить.','проверку человеком','сценарии отказа','границы данных','запасной вариант','Остановить']
    required[2]=('deploy/live/business.html',ru)
    required.append(('components/workshop/WorkshopBusiness.tsx',ru))
checks=0
for rel,needles in required:
    text=(ROOT/rel).read_text(encoding='utf-8')
    for n in needles:
        if n not in text:
            print(f'BUSINESS_DECISION_GATE_FAIL {rel}: missing {n}'); sys.exit(1)
        checks+=1
print(f'BUSINESS_DECISION_GATE_PASS checks={checks} surfaces=4')
