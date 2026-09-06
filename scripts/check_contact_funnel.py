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
for p in sorted(LIVE.rglob('*.html')):
 rel=p.relative_to(LIVE).as_posix();text=p.read_text(encoding='utf-8');parser=Links();parser.feed(text);checks+=1
 hits=[url for url in channels.values() if url in parser.hrefs or any(h.startswith(url+'?') for h in parser.hrefs)]
 if rel in {'start.html','en/start.html'}:
  for name,url in channels.items():
   checks+=1
   if not (url in parser.hrefs or any(h.startswith(url+'?') for h in parser.hrefs)):errors.append(f'{rel}: missing {name}')
  if text.count('briefSendLink')!=5:errors.append(f'{rel}: expected five briefSendLink hooks')
  if 'briefTelegramLink' in text:errors.append(f'{rel}: stale channel-specific hook')
 elif hits:errors.append(f'{rel}: direct channel anchors outside Start {hits}')
for p in sorted((ROOT/'app').rglob('page.tsx')):
 rel=p.relative_to(ROOT).as_posix();text=p.read_text(encoding='utf-8');checks+=1
 if any(v in text for v in channels.values()) or 'site.telegram' in text or 'site.whatsapp' in text or 'site.line' in text:
  errors.append(f'{rel}: direct external channel must be encapsulated by WorkshopStart')
channel=(ROOT/'components/workshop/ChannelLinks.tsx').read_text(encoding='utf-8')
for marker in ['site.telegram','site.email','site.whatsapp','site.line','id="contact-channels"']:
 checks+=1
 if marker not in channel:errors.append(f'ChannelLinks missing {marker}')
start=(ROOT/'components/workshop/WorkshopStart.tsx').read_text(encoding='utf-8');checks+=2
if '<ChannelLinks locale={locale}/>' not in start:errors.append('WorkshopStart missing ChannelLinks')
if 'contactHref="#contact-channels"' not in start:errors.append('WorkshopStart header CTA must remain same-page/internal')
for rel in ['components/ContactButtons.tsx','components/workshop/WorkshopHome.tsx','components/workshop/WorkshopPricing.tsx','components/workshop/WorkshopFamily.tsx','components/workshop/WorkshopAudience.tsx','components/workshop/WorkshopBusiness.tsx','components/workshop/WorkshopFaq.tsx','components/BusinessValueCalculator.tsx']:
 text=(ROOT/rel).read_text(encoding='utf-8');checks+=1
 if any(v in text for v in channels.values()) or 'site.telegram' in text:errors.append(f'{rel}: external channel leakage')
print(f'contact_funnel_checks={checks}')
if errors:
 for e in errors:print('FAIL:',e)
 sys.exit(1)
print('CONTACT_FUNNEL_PASS')
