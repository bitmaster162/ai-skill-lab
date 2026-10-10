#!/usr/bin/env python3
from pathlib import Path
import json
from source_paths import source_path
import sys, html
ROOT=Path(__file__).resolve().parents[1]
E32 = json.loads((ROOT / "deploy/live/_release.json").read_text(encoding="utf-8")).get("release_id")  in {'E3_2_RU_GLOSSARY_R1','E3_4_AI_SAFETY_AUDIENCE_R1','E3_5_HEADING_STRUCTURE_R1','E3_6_WORKSHOP_HERO_PANEL_R1'}
required={
 'app/projects/page.tsx':['EXAMPLE OUTPUTS · NOT TESTIMONIALS','не заявления о конкретных клиентах или учениках'],
 'app/en/projects/page.tsx':['EXAMPLE OUTPUTS · NOT TESTIMONIALS','not claims about specific clients or learners'],
 'components/ProjectStudio.tsx':['Детектив фактов','Мир и персонаж','Мини-игра','Fact detective','World & character','Mini game','Research OS','AI assistant prototype','Mini-product','Personal research workflow','Process prototype','AI operating rules'],
 'deploy/live/projects.html':['EXAMPLE OUTPUTS · NOT TESTIMONIALS','Детектив фактов','Мир и персонаж','Мини-игра','Research OS','AI assistant prototype','Mini-product','Personal research workflow','Process prototype','AI operating rules','не заявления о конкретных клиентах или учениках'],
 'deploy/live/en/projects.html':['EXAMPLE OUTPUTS · NOT TESTIMONIALS','Fact detective','World & character','Mini game','Research OS','AI assistant prototype','Mini-product','Personal research workflow','Process prototype','AI operating rules','not claims about specific clients or learners'],
 'app/about/page.tsx':['Proof by artifact','WORKFLOW','RESEARCH','BUILD','EXPLAIN','выдуманных отзывов','обещаний дохода','секретных промптов','сбора детских контактов'],
 'deploy/live/about.html':['Proof by artifact','WORKFLOW','RESEARCH','BUILD','EXPLAIN','выдуманных отзывов','обещаний дохода','секретных промптов','сбора детских контактов'],
 'app/en/about/page.tsx':['Proof by artifact','WORKFLOW','RESEARCH','BUILD','EXPLAIN','fabricated testimonials','guaranteed income','secret prompts','collecting a child'],
 'deploy/live/en/about.html':['Proof by artifact','WORKFLOW','RESEARCH','BUILD','EXPLAIN','fabricated testimonials','guaranteed income','secret prompts','collecting a child'],
}
problems=[]; n=0
E32_TRUST = {
 "EXAMPLE OUTPUTS · NOT TESTIMONIALS":"ПРИМЕРЫ РЕЗУЛЬТАТОВ · НЕ ОТЗЫВЫ",
 "Research OS":"Система исследования",
 "AI assistant prototype":"Прототип ИИ-помощника",
 "Mini-product":"Мини-продукт",
 "Personal research workflow":"Личный исследовательский процесс",
 "Process prototype":"Прототип рабочего процесса",
 "AI operating rules":"Правила работы с ИИ",
 "Proof by artifact":"Доказательство результатом",
 "WORKFLOW":"РАБОЧИЙ ПРОЦЕСС",
 "RESEARCH":"ИССЛЕДОВАНИЕ","BUILD":"СБОРКА","EXPLAIN":"ОБЪЯСНИТЬ",
}
for rel,needles in required.items():
 if E32 and rel in ("app/projects/page.tsx","deploy/live/projects.html","app/about/page.tsx","deploy/live/about.html"):
  needles=[E32_TRUST.get(x,x) for x in needles]
 text=html.unescape(source_path(ROOT, rel).read_text(encoding='utf-8')).lower()
 for needle in needles:
  n+=1
  if needle.lower() not in text: problems.append(f'{rel} missing {needle!r}')
if problems:
 for x in problems: print('FAIL:',x)
 sys.exit(1)
print(f'trust_route_parity_checks={n} surfaces={len(required)}')
print('TRUST_ROUTE_PARITY_PASS')
