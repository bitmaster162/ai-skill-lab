#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
errors=[]; checks=0

source=ROOT/'components'/'R77CommercialHome.tsx'
source_text=source.read_text(encoding='utf-8')
source_order=[
    'styles.hero',
    'styles.routeSection',
    'styles.businessBand',
    'styles.pricing',
    'styles.proofBand',
    'styles.finalCta',
]
positions=[]
for marker in source_order:
    checks+=1
    pos=source_text.find(marker)
    positions.append(pos)
    if pos < 0: errors.append(f'{source.relative_to(ROOT)}: missing {marker}')
checks+=1
if all(p >= 0 for p in positions) and positions != sorted(positions):
    errors.append(f'{source.relative_to(ROOT)}: commercial section order drift')
for marker in ['styles.heroPanel','LEARN','BUILD','BUSINESS','p("/start")','p("/business")','p("/proof")']:
    checks+=1
    if marker not in source_text: errors.append(f'{source.relative_to(ROOT)}: missing {marker}')

static_surfaces=[
    ('deploy/live/index.html','/start','/business','/proof'),
    ('deploy/live/en.html','/en/start','/en/business','/en/proof'),
]
for rel,start,business,proof in static_surfaces:
    t=(ROOT/rel).read_text(encoding='utf-8')
    markers=[
        'class="hero"',
        'class="routeSection"',
        'class="businessBand"',
        'class="pricing"',
        'class="proofBand"',
        'class="finalCta"',
    ]
    pos=[]
    for marker in markers:
        checks+=1
        idx=t.find(marker)
        pos.append(idx)
        if idx < 0: errors.append(f'{rel}: missing {marker}')
    checks+=1
    if all(p >= 0 for p in pos) and pos != sorted(pos):
        errors.append(f'{rel}: commercial section order drift')
    for href in [start,business,proof]:
        checks+=1
        if f'href="{href}"' not in t: errors.append(f'{rel}: missing CTA href {href}')
    for marker in ['class="heroPanel"','LEARN','BUILD','BUSINESS']:
        checks+=1
        if marker not in t: errors.append(f'{rel}: missing {marker}')

print(f'attention_hierarchy_checks={checks} source=1 static=2')
if errors:
    for e in errors: print('FAIL:',e)
    sys.exit(1)
print('ATTENTION_HIERARCHY_PASS')
