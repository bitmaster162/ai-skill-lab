#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
errors=[]; checks=0
source=(ROOT/'components/workshop/WorkshopHome.tsx').read_text(encoding='utf-8')

order=[
    'styles.hero',
    '<PromptAuditor locale={locale}',
    'styles.trackGrid',
    'styles.darkBand',
    '"CLEAR START"',
    'styles.proofBand',
    'styles.finalCta',
]
pos=[]
for marker in order:
    checks+=1
    p=source.find(marker); pos.append(p)
    if p<0: errors.append(f'WorkshopHome missing {marker}')
if all(p>=0 for p in pos) and pos!=sorted(pos):
    errors.append('WorkshopHome section order drift')

for marker in ['Find my route','Подобрать маршрут','Proof Lab','ADULTS','ВЗРОСЛЫЕ','BUSINESS','БИЗНЕС']:
    checks+=1
    if marker not in source: errors.append(f'WorkshopHome missing {marker}')

for rel,clear_start in [('deploy/live/index.html','ПОНЯТНЫЙ СТАРТ'),('deploy/live/en.html','CLEAR START')]:
    t=(ROOT/rel).read_text(encoding='utf-8')
    markers=['class="workshopHero"','data-prompt-auditor','class="trackGrid"','class="darkBand"',clear_start,'class="proofBand"','class="finalCta"']
    p=[]
    for marker in markers:
        checks+=1
        i=t.find(marker); p.append(i)
        if i<0: errors.append(f'{rel}: missing {marker}')
    if all(i>=0 for i in p) and p!=sorted(p):
        errors.append(f'{rel}: section order drift')

print(f'attention_hierarchy_checks={checks} source=1 static=2')
if errors:
    for e in errors: print('FAIL:',e)
    sys.exit(1)
print('ATTENTION_HIERARCHY_PASS')
