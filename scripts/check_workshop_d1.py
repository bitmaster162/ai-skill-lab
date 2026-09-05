#!/usr/bin/env python3
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1];LIVE=ROOT/'deploy/live';errors=[];checks=0
SURFACES=['index.html','en.html','start.html','en/start.html','pricing.html','en/pricing.html']
class A(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.forms=0
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=='a':self.links.append(d.get('href',''))
  if t=='form':self.forms+=1
for rel in SURFACES:
 path=LIVE/rel;text=path.read_text(encoding='utf-8');p=A();p.feed(text);checks+=1
 for marker in ['class="workshopPage"','class="workshopHeader"','class="workshopMenu"','class="workshopFooter"','id="lab-command"','src="/lab-command.js"']:
  checks+=1
  if marker not in text:errors.append(f'{rel}: missing {marker}')
 if p.forms:errors.append(f'{rel}: public form present')
 if any(h=='#' for h in p.links):errors.append(f'{rel}: placeholder href')
 if any(x in text for x in ['sc-for','sc-if','x-dc','support.js','fonts.googleapis.com','fonts.gstatic.com']):errors.append(f'{rel}: forbidden design-export primitive')
css=(LIVE/'workshop.css').read_text(encoding='utf-8')
for marker in ['#0b0d10','#12151a','#171b21','#1d222a','#2a3039','#606a78','#f5f7f9','#c3cad2','#919aa4','#d7dde3','#b9ff3f','#c9ff6b','#a5e82f','min-height:44px','prefers-reduced-motion:reduce']:
 checks+=1
 if marker not in css:errors.append(f'workshop.css missing {marker}')
for forbidden in ['box-shadow','translateY','scale(','@import','url(http']:
 checks+=1
 if forbidden in css:errors.append(f'workshop.css forbidden {forbidden}')
if '.trackCard:hover' not in css or 'background:var(--track)' not in css:errors.append('track hover fill missing')
if 'background:var(--acid)' not in css:errors.append('acid action token missing')
for marker in ['outline:3px solid var(--acid)','.trackCard:nth-child(1){--track:#8ab4ff}', '.trackCard:nth-child(2){--track:#5ee0c0}', '.trackCard:nth-child(3){--track:#c9a3ff}', '.trackCard:nth-child(4){--track:#f5f7f9}']:
 checks+=1
 if marker not in css:errors.append(f'workshop.css missing {marker}')
for rel in ['app/page.tsx','app/en/page.tsx']:
 checks+=1
 if '<WorkshopHome' not in (ROOT/rel).read_text(encoding='utf-8'):errors.append(f'{rel}: WorkshopHome mount missing')
for rel in ['app/start/page.tsx','app/en/start/page.tsx']:
 checks+=1
 if '<WorkshopStart' not in (ROOT/rel).read_text(encoding='utf-8'):errors.append(f'{rel}: WorkshopStart mount missing')
for rel in ['app/pricing/page.tsx','app/en/pricing/page.tsx']:
 checks+=1
 if '<WorkshopPricing' not in (ROOT/rel).read_text(encoding='utf-8'):errors.append(f'{rel}: WorkshopPricing mount missing')
facts=json.loads((ROOT/'data/commercial_facts.json').read_text(encoding='utf-8'));checks+=3
if facts.get('schema')!='ai-skill-lab.commercial-facts.v2':errors.append('commercial schema')
if facts.get('session_duration_minutes')!=60:errors.append('duration authority')
if facts.get('currency')!='USD':errors.append('currency authority')
manifest=json.loads((LIVE/'_release.json').read_text(encoding='utf-8'));checks+=1
if manifest.get('schema')!='ai-skill-lab.static-release.v1':errors.append('release schema drift')
print(f'workshop_d1_checks={checks} surfaces={len(SURFACES)}')
if errors:
 print('WORKSHOP_D1_FAIL');[print('-',e) for e in errors];sys.exit(1)
print('WORKSHOP_D1_PASS')
