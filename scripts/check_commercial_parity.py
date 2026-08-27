#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, sys

ROOT=Path(__file__).resolve().parents[1]
FACTS=json.loads((ROOT/'data/commercial_facts.json').read_text(encoding='utf-8'))

FILES={
    'pricing_ru':[ROOT/'app/pricing/page.tsx',ROOT/'deploy/live/pricing.html'],
    'pricing_en':[ROOT/'app/en/pricing/page.tsx',ROOT/'deploy/live/en/pricing.html'],
    'matcher_ru':[ROOT/'components/ProgramMatcher.tsx',ROOT/'deploy/live/matcher.html'],
    'matcher_en':[ROOT/'components/ProgramMatcher.tsx',ROOT/'deploy/live/en/matcher.html'],
    'adult_ru':[ROOT/'app/personal/page.tsx',ROOT/'deploy/live/personal.html'],
    'adult_en':[ROOT/'app/en/personal/page.tsx',ROOT/'deploy/live/en/personal.html'],
    'kids_ru':[ROOT/'app/kids/page.tsx',ROOT/'deploy/live/kids.html'],
    'kids_en':[ROOT/'app/en/kids/page.tsx',ROOT/'deploy/live/en/kids.html'],
    'teens_ru':[ROOT/'app/teens/page.tsx',ROOT/'deploy/live/teens.html'],
    'teens_en':[ROOT/'app/en/teens/page.tsx',ROOT/'deploy/live/en/teens.html'],
    'home_ru':[ROOT/'components/R77CommercialHome.tsx',ROOT/'deploy/live/index.html'],
    'home_en':[ROOT/'components/R77CommercialHome.tsx',ROOT/'deploy/live/en.html'],
    'parents_ru':[ROOT/'app/parents/page.tsx',ROOT/'deploy/live/parents.html'],
    'parents_en':[ROOT/'app/en/parents/page.tsx',ROOT/'deploy/live/en/parents.html'],
}

def read(p:Path)->str:
    if not p.exists(): raise FileNotFoundError(p)
    return p.read_text(encoding='utf-8')

texts={k:[(p,read(p)) for p in paths] for k,paths in FILES.items()}
problems=[]
checks=0
for track,plans in FACTS['tracks'].items():
    for plan in plans:
        for locale in ('ru','en'):
            needles=(plan['name'],plan['price'],plan[f'sessions_{locale}'])
            surfaces=[f'pricing_{locale}',f'matcher_{locale}',f'{track}_{locale}']
            if track == 'adult': surfaces.append(f'home_{locale}')
            if track in ('kids','teens'): surfaces.append(f'parents_{locale}')
            for surface in surfaces:
                for path,text in texts[surface]:
                    lower=text.lower()
                    for needle in needles:
                        checks += 1
                        if needle.lower() not in lower:
                            problems.append(f'{path.relative_to(ROOT)} missing {track}/{plan["id"]} {needle!r}')

family=FACTS['family']
for locale in ('ru','en'):
    needles=(family['name'],family['price'],family[f'sessions_{locale}'])
    for surface in (f'pricing_{locale}', f'home_{locale}', f'parents_{locale}'):
      for path,text in texts[surface]:
        lower=text.lower()
        for needle in needles:
            checks += 1
            if needle.lower() not in lower:
                problems.append(f'{path.relative_to(ROOT)} missing family {needle!r}')

for surface in ('matcher_ru','matcher_en'):
    for path,text in texts[surface]:
        checks += 1
        if FACTS['business']['display'].lower() not in text.lower():
            problems.append(f'{path.relative_to(ROOT)} missing business custom-scope display')

print(f'commercial_parity_checks={checks} packages={sum(len(v) for v in FACTS["tracks"].values())} files={sum(len(v) for v in FILES.values())}')
if problems:
    for p in problems: print('FAIL:',p)
    sys.exit(1)
print('COMMERCIAL_PARITY_PASS')
