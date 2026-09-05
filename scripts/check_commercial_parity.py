#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
FACTS=json.loads((ROOT/'data/commercial_facts.json').read_text(encoding='utf-8'))
errors=[];checks=0

def require(rel, needles):
 global checks
 text=(ROOT/rel).read_text(encoding='utf-8')
 for needle in needles:
  checks+=1
  if str(needle).casefold() not in text.casefold():errors.append(f'{rel}: missing {needle!r}')
 return text

expected_top={'schema':'ai-skill-lab.commercial-facts.v2','version':2,'currency':'USD','session_duration_minutes':60}
for key,value in expected_top.items():
 checks+=1
 if FACTS.get(key)!=value:errors.append(f'{key} drift {FACTS.get(key)!r}')
expected_numbers={
 ('diagnostic','price'):'$120',('diagnostic','credit_days'):14,
 ('business','workflow_audit','price'):'$890',('business','team_training','price_from_per_session'):'$390',
 ('business','team_training','max_people'):5,('business','team_training','min_sessions'):4,
 ('business','team_training','total_from'):'$1,560',('business','implementation_pilot','price_from'):'$4,900',
 ('business','implementation_pilot','scope_cap_hours'):35,
 ('recurring','operating_support','price_monthly'):'$490',('recurring','operating_support','hours'):4,
 ('recurring','operating_partner','price_monthly'):'$890',('recurring','operating_partner','hours'):8,
 ('recurring','office_hours','price_monthly'):'$178',('recurring','office_hours','sessions'):2,
 ('pair','multiplier'):1.6,('pair','participant_discount_percent'):20,
}
for path,value in expected_numbers.items():
 node=FACTS
 for key in path:node=node[key]
 checks+=1
 if node!=value:errors.append(f'authority {".".join(path)}={node!r}, expected {value!r}')
adapter=require('lib/commercial.ts',['commercialFacts = facts','sessionDurationMinutes','facts.schema !== "ai-skill-lab.commercial-facts.v2"','facts.session_duration_minutes !== 60'])

# Existing packages remain exact on legacy matcher/track/parent surfaces.
legacy={
 'adult':{'ru':['components/ProgramMatcher.tsx','deploy/live/matcher.html','app/personal/page.tsx','deploy/live/personal.html'],'en':['components/ProgramMatcher.tsx','deploy/live/en/matcher.html','app/en/personal/page.tsx','deploy/live/en/personal.html']},
 'kids':{'ru':['components/ProgramMatcher.tsx','deploy/live/matcher.html','app/kids/page.tsx','deploy/live/kids.html','app/parents/page.tsx','deploy/live/parents.html'],'en':['components/ProgramMatcher.tsx','deploy/live/en/matcher.html','app/en/kids/page.tsx','deploy/live/en/kids.html','app/en/parents/page.tsx','deploy/live/en/parents.html']},
 'teens':{'ru':['components/ProgramMatcher.tsx','deploy/live/matcher.html','app/teens/page.tsx','deploy/live/teens.html','app/parents/page.tsx','deploy/live/parents.html'],'en':['components/ProgramMatcher.tsx','deploy/live/en/matcher.html','app/en/teens/page.tsx','deploy/live/en/teens.html','app/en/parents/page.tsx','deploy/live/en/parents.html']},
}
for track,plans in FACTS['tracks'].items():
 for plan in plans:
  for locale in ('ru','en'):
   for rel in legacy[track][locale]:require(rel,[plan['name'],plan['price'],plan[f'sessions_{locale}']])
family=FACTS['family']
for locale,paths in {
 'ru':['app/parents/page.tsx','deploy/live/parents.html','deploy/live/family.html'],
 'en':['app/en/parents/page.tsx','deploy/live/en/parents.html','deploy/live/en/family.html'],
}.items():
 for rel in paths:require(rel,[family['name'],family['price'],family[f'sessions_{locale}']])
for rel in ['components/ProgramMatcher.tsx','deploy/live/matcher.html','deploy/live/en/matcher.html']:
 require(rel,[FACTS['business']['display']])

# Workshop source binds to the typed authority; static output carries exact rendered facts.
require('components/workshop/WorkshopHome.tsx',['commercialFacts.tracks.adult','commercialFacts.family','sessionDurationMinutes','adult.map','family.price'])
require('components/workshop/WorkshopFamily.tsx',['commercialFacts.family','sessionDurationMinutes','ONE LEARNER','ОДИН УЧЕНИК','14 ×'])
require('components/workshop/WorkshopPricing.tsx',[
 'commercialFacts.tracks.adult','commercialFacts.tracks.kids','commercialFacts.tracks.teens','commercialFacts.diagnostic',
 'business.workflow_audit.price','business.team_training.price_from_per_session','business.team_training.total_from',
 'business.implementation_pilot.price_from','business.implementation_pilot.scope_cap_hours',
 'recurring.operating_support.price_monthly','recurring.operating_partner.price_monthly','recurring.office_hours.price_monthly',
 'pair.multiplier','pair.participant_discount_percent','sessionDurationMinutes',
])
require('app/pricing/page.tsx',['<WorkshopPricing locale="ru"/>'])
require('app/en/pricing/page.tsx',['<WorkshopPricing locale="en"/>'])
for locale,home,pricing in [('ru','deploy/live/index.html','deploy/live/pricing.html'),('en','deploy/live/en.html','deploy/live/en/pricing.html')]:
 for plan in FACTS['tracks']['adult']:
  require(home,[plan['name'],plan['price'],plan[f'sessions_{locale}']])
 require(home,[family['name'],family['price'],family[f'sessions_{locale}']])
 for plans in FACTS['tracks'].values():
  for plan in plans:require(pricing,[plan['name'],plan['price'],plan[f'sessions_{locale}']])
 require(pricing,[family['name'],family['price'],family[f'sessions_{locale}'],'$120','$890','$390','$1,560','$4,900','35','$490','$178','20%'])
 if locale=='en':require(pricing,['14 days','5 people','4 sessions','1.6×'])
 else:require(pricing,['14 дней','5 человек','4 занятия','1,6×'])
for rel in ['components/workshop/WorkshopPricing.tsx','deploy/live/pricing.html','deploy/live/en/pricing.html']:
 text=(ROOT/rel).read_text(encoding='utf-8')
 for marker in ['$89/hour','$89 / hour','$89 в час']:
  checks+=1
  if marker in text:errors.append(f'{rel}: publishes internal hourly math')
print(f'commercial_parity_checks={checks} packages={sum(len(v) for v in FACTS["tracks"].values())} schema=v2')
if errors:
 for e in errors:print('FAIL:',e)
 sys.exit(1)
print('COMMERCIAL_PARITY_PASS')
