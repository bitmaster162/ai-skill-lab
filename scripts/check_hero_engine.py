#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];errors=[];checks=0
component=(ROOT/'components/HeroEngine.tsx').read_text(encoding='utf-8')
for marker in ['AI SKILL ENGINE','research','build','automate','verify','SOURCE-BACKED','SHIPPABLE','REPEATABLE','RELEASE-GATED','DECISION BRIEF','PROTOTYPE','WORKFLOW','RECEIPT']:
 checks+=1
 if marker.lower() not in component.lower():errors.append(f'HeroEngine source missing {marker!r}')
for rel,en in [('app/page.tsx',False),('app/en/page.tsx',True)]:
 text=(ROOT/rel).read_text(encoding='utf-8');checks+=1
 expected='<HeroEngine locale="en" />' if en else '<HeroEngine />'
 if expected not in text:errors.append(f'{rel}: HeroEngine not mounted')
for rel in ['deploy/live/index.html','deploy/live/en.html']:
 text=(ROOT/rel).read_text(encoding='utf-8')
 for marker in ['AI SKILL ENGINE','data-hero-engine','data-engine-key="research"','data-engine-key="build"','data-engine-key="automate"','data-engine-key="verify"','engine-signal','engine-mode','engine-human','engine-ship']:
  checks+=1
  if marker not in text:errors.append(f'{rel}: missing {marker!r}')
 checks+=1
 if text.count('data-engine-key=')!=4:errors.append(f'{rel}: expected 4 engine buttons')
corpus=component+'\n'+(ROOT/'deploy/live/index.html').read_text()+'\n'+(ROOT/'deploy/live/en.html').read_text()
for bad in ['live model call','hidden AI call','sends your input','отправляет ваш ввод']:
 checks+=1
 if bad.lower() in corpus.lower():errors.append(f'hero engine forbidden claim {bad!r}')
if errors:
 print(f'hero_engine_checks={checks}');[print('FAIL:',e) for e in errors];sys.exit(1)
print(f'hero_engine_checks={checks} static_pages=2 modes=4')
print('HERO_ENGINE_PARITY_PASS')
