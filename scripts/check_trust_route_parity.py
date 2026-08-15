#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
required={
 'app/projects/page.tsx':['EXAMPLE OUTPUTS · NOT TESTIMONIALS','Детектив фактов','Мир и персонаж','Мини-игра','Research OS','AI assistant prototype','Mini-product','Personal research workflow','Process prototype','AI operating rules','не заявления о конкретных клиентах или учениках'],
 'deploy/live/projects.html':['EXAMPLE OUTPUTS · NOT TESTIMONIALS','Детектив фактов','Мир и персонаж','Мини-игра','Research OS','AI assistant prototype','Mini-product','Personal research workflow','Process prototype','AI operating rules','не заявления о конкретных клиентах или учениках'],
 'app/en/projects/page.tsx':['EXAMPLE OUTPUTS · NOT TESTIMONIALS','Fact detective','World & character','Mini game','Research OS','AI assistant prototype','Mini-product','Personal research workflow','Process prototype','AI operating rules','not claims about specific clients or learners'],
 'deploy/live/en/projects.html':['EXAMPLE OUTPUTS · NOT TESTIMONIALS','Fact detective','World & character','Mini game','Research OS','AI assistant prototype','Mini-product','Personal research workflow','Process prototype','AI operating rules','not claims about specific clients or learners'],
 'app/about/page.tsx':['Proof by artifact','WORKFLOW','RESEARCH','BUILD','EXPLAIN','выдуманных отзывов','обещаний дохода','секретных промптов','сбора детских контактов'],
 'deploy/live/about.html':['Proof by artifact','WORKFLOW','RESEARCH','BUILD','EXPLAIN','выдуманных отзывов','обещаний дохода','секретных промптов','сбора детских контактов'],
 'app/en/about/page.tsx':['Proof by artifact','WORKFLOW','RESEARCH','BUILD','EXPLAIN','fabricated testimonials','guaranteed income','secret prompts','collecting a child'],
 'deploy/live/en/about.html':['Proof by artifact','WORKFLOW','RESEARCH','BUILD','EXPLAIN','fabricated testimonials','guaranteed income','secret prompts','collecting a child'],
}
problems=[]; n=0
for rel,needles in required.items():
 text=(ROOT/rel).read_text(encoding='utf-8').lower()
 for needle in needles:
  n+=1
  if needle.lower() not in text: problems.append(f'{rel} missing {needle!r}')
if problems:
 for x in problems: print('FAIL:',x)
 sys.exit(1)
print(f'trust_route_parity_checks={n} surfaces={len(required)}')
print('TRUST_ROUTE_PARITY_PASS')
