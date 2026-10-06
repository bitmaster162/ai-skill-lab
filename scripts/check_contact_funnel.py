#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];LIVE=ROOT/'deploy/live';errors=[];checks=0
channels={'telegram':'https://t.me/BiTFormer','email':'mailto:robert@aiskillab.work','whatsapp':'https://wa.me/66649701204','line':'https://line.me/ti/p/~iwf555'}
class Links(HTMLParser):
 def __init__(self):super().__init__();self.hrefs=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.hrefs.append(dict(attrs).get('href',''))
light={'privacy.html','terms.html','en/privacy.html','en/terms.html'}
start_routes={'start.html','en/start.html'}
e14_reach_routes={'index.html','en.html','kids.html','en/kids.html','teens.html','en/teens.html','parents.html','en/parents.html','personal.html','en/personal.html','business.html','en/business.html','pricing.html','en/pricing.html','matcher.html','en/matcher.html'}
reach_routes=0
for p in sorted(LIVE.rglob('*.html')):
 rel=p.relative_to(LIVE).as_posix();text=p.read_text(encoding='utf-8');parser=Links();parser.feed(text);checks+=1
 counts={name:sum(1 for h in parser.hrefs if h==url or h.startswith(url+'?')) for name,url in channels.items()}
 if rel in start_routes:
  for name,count in counts.items():
   checks+=1
   if count<1:errors.append(f'{rel}: missing {name}')
  if text.count('briefSendLink')!=5:errors.append(f'{rel}: expected five briefSendLink hooks')
  if 'briefTelegramLink' in text:errors.append(f'{rel}: stale channel-specific hook')
  if 'class="reachBlock"' in text:errors.append(f'{rel}: duplicate D1 reach block')
 elif rel in light:
  checks+=1
  if any(counts.values()):errors.append(f'{rel}: direct channels forbidden on legal light page {counts}')
  if 'class="reachBlock"' in text:errors.append(f'{rel}: D1 reach block forbidden on legal light page')
 elif rel!='404.html':
  reach_routes+=1
  for name,count in counts.items():
   checks+=1
   expected=2 if rel in e14_reach_routes and name in {'telegram','whatsapp'} else 1
   if count!=expected:errors.append(f'{rel}: approved contact {name} count={count}, expected {expected}')
  block_count=text.count('class="reachBlock"')
  if block_count!=1:errors.append(f'{rel}: D1 reach block count={block_count}, expected 1')
checks+=1
if reach_routes!=46:errors.append(f'D1 reach-route count={reach_routes}, expected 46')
for p in sorted((ROOT/'app').rglob('page.tsx')):
 rel=p.relative_to(ROOT).as_posix();text=p.read_text(encoding='utf-8');checks+=1
 if any(v in text for v in channels.values()) or 'site.telegram' in text or 'site.whatsapp' in text or 'site.line' in text:
  errors.append(f'{rel}: direct external channel must be encapsulated by WorkshopStart')
channel=(ROOT/'components/workshop/ChannelLinks.tsx').read_text(encoding='utf-8')
for marker in ['site.telegram','site.email','site.whatsapp','site.line','id="contact-channels"']:
 checks+=1
 if marker not in channel:errors.append(f'ChannelLinks missing {marker}')
start=(ROOT/'components/workshop/WorkshopStart.tsx').read_text(encoding='utf-8');checks+=4
if '<ChannelLinks locale={locale}/>' not in start:errors.append('WorkshopStart missing ChannelLinks')
if 'showReach={false}' not in start:errors.append('WorkshopStart must suppress duplicate D1 reach block')
if 'contactHref=' in start:errors.append('WorkshopStart header CTA must use canonical /start route, not a fragment override')
if 'Reply within 1–2 business days.' not in start or 'Ответ в течение 1–2 рабочих дней.' not in start:errors.append('WorkshopStart missing approved D1 reply time')
shell=(ROOT/'components/workshop/WorkshopShell.tsx').read_text(encoding='utf-8')
checks+=10
for url in channels.values():
 if shell.count(url)!=1:errors.append(f'WorkshopShell approved D1 channel count for {url}={shell.count(url)}, expected 1')
for marker in ['showReach ? <ReachBlock locale={locale} /> : null','Как написать','How to reach us','Ответ в течение 1–2 рабочих дней.','Reply within 1–2 business days.','href={en ? "/en/start" : "/start"}']:
 if marker not in shell:errors.append(f'WorkshopShell missing D1 contact marker {marker!r}')
business=(ROOT/'components/workshop/WorkshopBusiness.tsx').read_text(encoding='utf-8');checks+=1
if 'contactHref=' in business:errors.append('WorkshopBusiness header CTA must use canonical /start route, not business fragment')
for rel in ['components/ContactButtons.tsx','components/workshop/WorkshopHome.tsx','components/workshop/WorkshopPricing.tsx','components/workshop/WorkshopFamily.tsx','components/workshop/WorkshopAudience.tsx','components/workshop/WorkshopBusiness.tsx','components/workshop/WorkshopFaq.tsx','components/BusinessValueCalculator.tsx']:
 text=(ROOT/rel).read_text(encoding='utf-8');checks+=1
 if any(v in text for v in channels.values()) or 'site.telegram' in text:errors.append(f'{rel}: external channel leakage')
print(f'contact_funnel_checks={checks}')
if errors:
 for e in errors:print('FAIL:',e)
 sys.exit(1)
print('CONTACT_FUNNEL_PASS')
