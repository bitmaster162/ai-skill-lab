#!/usr/bin/env python3
from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parents[1];LIVE=ROOT/'deploy/live';README=ROOT/'README.md';errors=[];checks=0
WORKSHOP={'index.html': ('/start', '/en', False), 'en.html': ('/en/start', '/', True), 'start.html': ('#contact-channels', '/en/start', False), 'en/start.html': ('#contact-channels', '/start', True), 'pricing.html': ('/start', '/en/pricing', False), 'en/pricing.html': ('/en/start', '/pricing', True), 'family.html': ('/start', '/en/family', False), 'en/family.html': ('/en/start', '/family', True), 'personal.html': ('/start', '/en/personal', False), 'teens.html': ('/start', '/en/teens', False), 'kids.html': ('/start', '/en/kids', False), 'business.html': ('/start#business-brief', '/en/business', False), 'faq.html': ('/start', '/en/faq', False), 'en/personal.html': ('/en/start', '/personal', True), 'en/teens.html': ('/en/start', '/teens', True), 'en/kids.html': ('/en/start', '/kids', True), 'en/business.html': ('/en/start#business-brief', '/business', True), 'en/faq.html': ('/en/start', '/faq', True)}
public=set();legacy=0
for p in sorted(LIVE.rglob('*.html')):
 if p.name=='404.html':continue
 rel=p.relative_to(LIVE).as_posix();route='/' if rel=='index.html' else '/en' if rel=='en.html' else '/'+rel[:-5];public.add(route);text=p.read_text(encoding='utf-8')
 if rel in WORKSHOP:
  start,alternate,en=WORKSHOP[rel];checks+=1
  m=re.search(r'<header class="workshopHeader">(.*?)</header>',text,re.S)
  if not m:errors.append(f'{rel}: workshop header missing');continue
  h=m.group(1);expected=[f'/en{x}' for x in ['/personal','/teens','/kids','/business','/studio','/pricing']] if en else ['/personal','/teens','/kids','/business','/studio','/pricing']
  for href in expected:
   checks+=1
   if h.count(f'href="{href}"')!=1:errors.append(f'{rel}: workshop menu {href} count drift')
  for marker in ['data-lab-command-open','aria-label="Proof Lab"',f'href="{alternate}"',f'href="{start}"']:
   checks+=1
   if marker not in h:errors.append(f'{rel}: missing {marker}')
  if '<header class="nav">' in text:errors.append(f'{rel}: legacy header returned')
 else:
  legacy+=1;en=rel.startswith('en/');expected=[f'/en{x}' for x in ['/personal','/business','/kids','/teens','/pricing','/about','/faq']] if en else ['/personal','/business','/kids','/teens','/pricing','/about','/faq']
  m=re.search(r'<header class="nav">(.*?)</header>',text,re.S);checks+=1
  if not m:errors.append(f'{rel}: legacy nav missing');continue
  h=m.group(1)
  for href in expected:
   checks+=1
   if h.count(f'href="{href}"')!=2:errors.append(f'{rel}: legacy menu {href} count drift')
source=(ROOT/'components/workshop/WorkshopShell.tsx').read_text(encoding='utf-8')
for label in ['Взрослые','Подростки','Дети','Бизнес','Studio','Цены','Adults','Teens','Kids','Business','Pricing']:
 checks+=1
 if label not in source:errors.append(f'WorkshopShell missing {label}')
for forbidden in ['Взрослым','Стоимость','Дети 8–13','Подростки 14–18']:
 checks+=1
 if f'[["{forbidden}"' in source:errors.append(f'Workshop menu stale label {forbidden}')
readme=README.read_text(encoding='utf-8')
for label,expected in [('RU',{r for r in public if r=='/' or not r.startswith('/en')}),('EN',{r for r in public if r=='/en' or r.startswith('/en/')})]:
 m=re.search(rf'^- {label}: (.+)$',readme,re.M);checks+=1
 if not m:errors.append(f'README missing {label} inventory')
 elif set(re.findall(r'`([^`]+)`',m.group(1)))!=expected:errors.append(f'README {label} inventory drift')
print(f'navigation_parity_checks={checks} workshop_pages={len(WORKSHOP)} legacy_pages={legacy}')
if errors:
 for e in errors:print('FAIL:',e)
 sys.exit(1)
print('NAVIGATION_PARITY_PASS')
