#!/usr/bin/env python3
from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parents[1]
scan=[*ROOT.joinpath('app').rglob('*.tsx'),*ROOT.joinpath('components').rglob('*.tsx'),*ROOT.joinpath('deploy/live').rglob('*.html')]
rx=re.compile(r'\b(?:\d{2,3}\s*[–-]\s*\d{2,3}|\d{2,3})(?:\s*[-–]\s*|\s+)(?:минут(?:ы|у)?|minutes?)\b',re.I)
errors=[];claims=[]
for p in scan:
 text=p.read_text(encoding='utf-8')
 for m in rx.finditer(text):
  claim=m.group(0);claims.append((p.relative_to(ROOT).as_posix(),claim))
  normalized=' '.join(re.sub(r'[-–]+',' ',claim.casefold()).split())
  if normalized not in {'60 минут','60 minute','60 minutes'}:errors.append(f'{p.relative_to(ROOT)}: conflicting duration {claim!r}')
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
 text=(ROOT/rel).read_text(encoding='utf-8')
 for needle in needles:
  checks+=1
  if needle not in text:errors.append(f'{rel}: missing {needle!r}')
if not claims:errors.append('no numeric duration claims found')
print(f'session_duration_checks={checks} claims={len(claims)} authority=60')
if errors:
 print('SESSION_DURATION_POLICY_FAIL');[print('-',e) for e in errors];sys.exit(1)
print('SESSION_DURATION_POLICY_PASS')
