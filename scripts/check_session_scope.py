#!/usr/bin/env python3
from pathlib import Path
from source_paths import source_path
import re,sys,json
ROOT=Path(__file__).resolve().parents[1]
scan=[*ROOT.joinpath('app').rglob('*.tsx'),*ROOT.joinpath('components').rglob('*.tsx'),*ROOT.joinpath('deploy/live').rglob('*.html')]
rx=re.compile(r'\b(?:\d{2,3}\s*[–-]\s*\d{2,3}|\d{2,3})(?:\s*[-–]\s*|\s+)(?:минут(?:ы|у)?|minutes?)\b',re.I)
errors=[];claims=[];intro_claims=0
# E3.1 SEO copy is approved byte-for-byte and describes a free intro call.
# Exclude only exact metadata-description spans, not arbitrary body claims.
SEO_DESCRIPTIONS = {}
release = json.loads((ROOT/'deploy/live/_release.json').read_text(encoding='utf-8')).get('release_id')
if release in {'E3_1_RU_SEO_R1','E3_3_H1_ACTION_R1','E3_2_RU_GLOSSARY_R1','E3_4_AI_SAFETY_AUDIENCE_R1'}:
 from check_e3_1_ru_seo import EXACT
 for route,(_title,description) in EXACT.items():
  source_rel = 'app/(ru)/' + (route.strip('/') + '/' if route != '/' else '') + 'page.tsx'
  static_rel = 'deploy/live/' + (route.strip('/') + '.html' if route != '/' else 'index.html')
  SEO_DESCRIPTIONS[source_rel] = description
  SEO_DESCRIPTIONS[static_rel] = description
for p in scan:
 text=p.read_text(encoding='utf-8')
 rel=p.relative_to(ROOT).as_posix()
 seo_description=SEO_DESCRIPTIONS.get(rel)
 seo_spans=[(m.start(),m.end()) for m in re.finditer(re.escape(seo_description),text)] if seo_description else []
 e33_h1={
  "components/workshop/WorkshopStart.tsx":'<h1>{en ? <>Start with a free<br/><em>15-minute call.</em></> : <>Начните с бесплатного звонка<br/><em>на 15 минут.</em></>}</h1>',
  "deploy/live/start.html":'<h1>Начните с бесплатного звонка<br><em>на 15 минут.</em></h1>',
  "deploy/live/en/start.html":'<h1>Start with a free<br><em>15-minute call.</em></h1>',
 } if release in {"E3_3_H1_ACTION_R1","E3_2_RU_GLOSSARY_R1","E3_4_AI_SAFETY_AUDIENCE_R1"} else {}
 approved_h1=e33_h1.get(rel)
 h1_spans=[]
 if approved_h1:
  if text.count(approved_h1)!=1:errors.append(f"{rel}: E3.3 free intro call H1 contract drift")
  h1_spans=[(m.start(),m.end()) for m in re.finditer(re.escape(approved_h1),text)]
 for m in rx.finditer(text):
  if any(start<=m.start() and m.end()<=end for start,end in [*seo_spans,*h1_spans]):
   continue
  claim=m.group(0);claims.append((rel,claim))
  normalized=' '.join(re.sub(r'[-–]+',' ',claim.casefold()).split())
  if normalized in {'60 минут','60 minute','60 minutes'}:continue
  if normalized in {'15 минут','15 minute','15 minutes'}:
   window=text[max(0,m.start()-320):min(len(text),m.end()+320)].casefold()
   if any(marker in window for marker in ('data-e14-entry','data-intro-call-channel','звонок-знакомство','intro call','intro-call')):
    intro_claims+=1;continue
  errors.append(f'{p.relative_to(ROOT)}: conflicting duration {claim!r}')
required={
 'data/commercial_facts.json':['"session_duration_minutes": 60'],
 'lib/commercial.ts':['facts.session_duration_minutes !== 60','Session duration authority must be 60 minutes'],
 'components/workshop/WorkshopHome.tsx':['sessionDurationMinutes','minutes','минут'],
 'components/workshop/WorkshopStart.tsx':['sessionDurationMinutes','minutes','минут'],
 'components/workshop/WorkshopPricing.tsx':['sessionDurationMinutes','minutes','минут'],
 'deploy/live/index.html':['60 минут'],'deploy/live/en.html':['60 minutes'],
 'deploy/live/start.html':['60 минут'],'deploy/live/en/start.html':['60 minutes'],
 'deploy/live/pricing.html':['60 минут'],'deploy/live/en/pricing.html':['60 minutes'],
 'app/faq/page.tsx':['60 минут'],'app/en/faq/page.tsx':['60 minutes'],
 'deploy/live/faq.html':['60 минут'],'deploy/live/en/faq.html':['60 minutes'],
 'components/workshop/WorkshopAudience.tsx':['sessionDurationMinutes','минут','minutes'],
 'components/workshop/WorkshopBusiness.tsx':['sessionDurationMinutes','минут','minute'],
 'deploy/live/kids.html':['60 минут'],'deploy/live/en/kids.html':['60 minutes'],
 'components/workshop/WorkshopFamily.tsx':['sessionDurationMinutes','MINUTES','МИНУТ'],
 'deploy/live/family.html':['60 МИНУТ'],'deploy/live/en/family.html':['60 MINUTES'],
}
checks=0
for rel,needles in required.items():
 text=source_path(ROOT, rel).read_text(encoding='utf-8')
 for needle in needles:
  checks+=1
  if needle not in text:errors.append(f'{rel}: missing {needle!r}')
if not claims:errors.append('no numeric duration claims found')
if intro_claims!=36:errors.append(f'E1.4 intro-call duration claims {intro_claims} != 36')
print(f'session_duration_checks={checks} claims={len(claims)} authority=60 intro_call=15 intro_claims={intro_claims}')
if errors:
 print('SESSION_DURATION_POLICY_FAIL');[print('-',e) for e in errors];sys.exit(1)
print('SESSION_DURATION_POLICY_PASS')
