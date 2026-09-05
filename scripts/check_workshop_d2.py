#!/usr/bin/env python3
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import json,re,sys
ROOT=Path(__file__).resolve().parents[1];LIVE=ROOT/'deploy/live';ORIGIN='https://ai-skill-lab.vercel.app'
errors=[];checks=0
class Audit(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.hrefs=[];self.forms=0;self.h1=0;self.ids=set();self.styles=[];self.canonical=[];self.alts={}
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='a' and a.get('href'):self.hrefs.append(a['href'])
  if tag=='form':self.forms+=1
  if tag=='h1':self.h1+=1
  if a.get('id'):self.ids.add(a['id'])
  if tag=='link' and a.get('rel')=='stylesheet':self.styles.append(a.get('href',''))
  if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href',''))
  if tag=='link' and a.get('rel')=='alternate':self.alts[a.get('hreflang','')]=a.get('href','')
def route_for(p):
 rel=p.relative_to(LIVE).as_posix()
 return '/' if rel=='index.html' else '/en' if rel=='en.html' else '/'+rel[:-5]
def lum(h):
 c=[int(h[i:i+2],16)/255 for i in (1,3,5)];v=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in c]
 return .2126*v[0]+.7152*v[1]+.0722*v[2]
def ratio(a,b):
 x,y=sorted((lum(a),lum(b)),reverse=True);return (x+.05)/(y+.05)
def need(rel,tokens):
 global checks
 text=(ROOT/rel).read_text(encoding='utf-8')
 for token in tokens:
  checks+=1
  if token not in text:errors.append(f'{rel}: missing {token!r}')
 return text
source=need('components/workshop/WorkshopFamily.tsx',[
 'commercialFacts.family','sessionDurationMinutes','FAMILY FORMAT · ONE LEARNER','СЕМЕЙНЫЙ ФОРМАТ · ОДИН УЧЕНИК',
 '12 learner sessions','12 занятий с учеником','2 parent sessions','2 занятия с родителем',
 'Household rules','Домашние правила','Final presentation','Финальная защита',
 'Organizational communication stays with an adult.','Организационную переписку ведёт взрослый.',
 'href={start}','href="#included"','ONE LEARNER · 14 ×','ОДИН УЧЕНИК · 14 ×'])
for forbidden in ['t.me/','wa.me/','line.me/','mailto:','<form','[response time]','[срок ответа]','x-dc','sc-for','sc-if','support.js','fonts.googleapis.com','fonts.gstatic.com']:
 checks+=1
 if forbidden in source:errors.append(f'WorkshopFamily source forbidden {forbidden!r}')
need('app/family/page.tsx',['<WorkshopFamily locale="ru"/>','canonical: "/family"','en: "/en/family"'])
need('app/en/family/page.tsx',['<WorkshopFamily locale="en"/>','canonical: "/en/family"','ru: "/family"'])
source_css=need('components/workshop/WorkshopShell.module.css',['.familyCard{','#ff9ecb','#2b0a1c','#241522','.familyHero{','.familyIncludedGrid{','.familyRuleGrid{','prefers-reduced-motion:reduce'])
static_css=need('deploy/live/workshop.css',['.familyCard{','#ff9ecb','#2b0a1c','#241522','.familyHero{','.familyIncludedGrid{','.familyRuleGrid{','prefers-reduced-motion:reduce'])
for name,css in [('source',source_css),('static',static_css)]:
 for forbidden in ['box-shadow','translateY(','scale(','@import','url(http','fonts.googleapis.com','fonts.gstatic.com']:
  checks+=1
  if forbidden in css:errors.append(f'{name} Family CSS forbidden {forbidden!r}')
for bg in ['#2b0a1c','#241522']:
 checks+=1
 if ratio('#ff9ecb',bg)<4.5:errors.append(f'Family token contrast {bg}={ratio("#ff9ecb",bg):.2f}')
pages={
 'deploy/live/family.html':{'route':'/family','alt':'/en/family','start':'/start','tokens':['СЕМЕЙНЫЙ ФОРМАТ · ОДИН УЧЕНИК','Учится ребёнок.','Правила заводит семья.','12 занятий + 2 сессии родителю','ОДИН УЧЕНИК · 14 × 60 МИНУТ','Домашние правила','Финальная защита','Организационную переписку ведёт взрослый.']},
 'deploy/live/en/family.html':{'route':'/en/family','alt':'/family','start':'/en/start','tokens':['FAMILY FORMAT · ONE LEARNER','The child learns.','The household sets the rules.','12 learner sessions + 2 parent sessions','ONE LEARNER · 14 × 60 MINUTES','Household rules','Final presentation','Organizational communication stays with an adult.']},
}
for rel,cfg in pages.items():
 text=need(rel,cfg['tokens']);a=Audit();a.feed(text);checks+=8
 expected=ORIGIN+cfg['route']
 if a.forms:errors.append(f'{rel}: public form present')
 if a.h1!=1:errors.append(f'{rel}: h1 count {a.h1}')
 if not {'main','included'}<=a.ids:errors.append(f'{rel}: required ids missing')
 if a.styles!=['/workshop.css']:errors.append(f'{rel}: stylesheet drift {a.styles}')
 if a.canonical!=[expected]:errors.append(f'{rel}: canonical drift {a.canonical}')
 if a.alts!={'ru':ORIGIN+'/family','en':ORIGIN+'/en/family','x-default':ORIGIN+'/family'}:errors.append(f'{rel}: hreflang drift {a.alts}')
 if cfg['start'] not in a.hrefs or cfg['alt'] not in a.hrefs or '#included' not in a.hrefs:errors.append(f'{rel}: internal CTA/alternate drift')
 if any(urlparse(h).scheme or h.startswith('//') for h in a.hrefs):errors.append(f'{rel}: external anchor present')
 for forbidden in ['t.me/','wa.me/','line.me/','mailto:','href="#"','[response time]','[срок ответа]','x-dc','sc-for','sc-if','support.js','fonts.googleapis.com','fonts.gstatic.com']:
  checks+=1
  if forbidden in text:errors.append(f'{rel}: forbidden {forbidden!r}')
routes={route_for(p) for p in LIVE.rglob('*.html') if p.name!='404.html'}
ru={r for r in routes if r=='/' or not r.startswith('/en')};en={r for r in routes if r=='/en' or r.startswith('/en/')};checks+=5
if len(routes)!=46:errors.append(f'route authority {len(routes)} != 46')
if len(ru)!=23 or len(en)!=23:errors.append(f'locale route authority RU={len(ru)} EN={len(en)}')
if not {'/family','/en/family'}<=routes:errors.append('Family route pair missing')
html_files=list(LIVE.rglob('*.html'))
if len(html_files)!=47:errors.append(f'static HTML count {len(html_files)} != 47')
sitemap=(LIVE/'sitemap.xml').read_text(encoding='utf-8');locs=set(re.findall(r'<loc>(https?://[^<]+)</loc>',sitemap));expected={ORIGIN+('/' if r=='/' else r) for r in routes};checks+=2
if locs!=expected:errors.append(f'sitemap authority mismatch missing={sorted(expected-locs)} extra={sorted(locs-expected)}')
llms=(LIVE/'llms.txt').read_text(encoding='utf-8');checks+=3
for marker in ['[RU](https://ai-skill-lab.vercel.app/family)','[EN](https://ai-skill-lab.vercel.app/en/family)']:
 if marker not in llms:errors.append(f'llms.txt missing {marker}')
if len(re.findall(r'\]\((https?://[^)]+)\)',llms))!=46:errors.append('llms.txt URL count drift')
readme=(ROOT/'README.md').read_text(encoding='utf-8');checks+=2
for route in ['`/family`','`/en/family`']:
 if readme.count(route)!=1:errors.append(f'README route inventory {route} count={readme.count(route)}')
next_sitemap=(ROOT/'app/sitemap.ts').read_text(encoding='utf-8');checks+=2
for route in ['"/family"','"/en/family"']:
 if next_sitemap.count(route)!=1:errors.append(f'Next sitemap {route} count={next_sitemap.count(route)}')
need('components/workshop/WorkshopHome.tsx',['href={p("/family")}','styles.familyCard'])
need('components/workshop/WorkshopPricing.tsx',['href={p("/family")}','Open Family route','Открыть Family'])
for rel,href in [('deploy/live/index.html','/family'),('deploy/live/en.html','/en/family'),('deploy/live/pricing.html','/family'),('deploy/live/en/pricing.html','/en/family')]:
 text=(ROOT/rel).read_text(encoding='utf-8');checks+=1
 actual=text.count('href="'+href+'"')
 if actual!=1:errors.append(f'{rel}: Family inbound link count={actual}')
for rel in ['deploy/live/r70-broadsheet.css','deploy/live/r77-commercial.css']:
 checks+=1
 if (ROOT/rel).is_file():errors.append(f'unreferenced static asset present: {rel}')
checks+=1
if not (ROOT/'deploy/live/r77-commercial-mobile.css').is_file():errors.append('active r77-commercial-mobile.css missing')
manifest=json.loads((LIVE/'_release.json').read_text(encoding='utf-8'));checks+=5
if manifest.get('schema')!='ai-skill-lab.static-release.v1':errors.append('release manifest schema drift')
# Current release identity is owned by the D3 release checker.
if manifest.get('file_count')!=62:errors.append(f'manifest file_count {manifest.get("file_count")} != 62')
listed={x.get('path') for x in manifest.get('files',[])}
if not {'family.html','en/family.html'}<=listed:errors.append('manifest missing Family static pages')
if {'r70-broadsheet.css','r77-commercial.css'}&listed:errors.append('manifest contains unreferenced assets')
if 'r77-commercial-mobile.css' not in listed:errors.append('manifest missing active mobile CSS')
print(f'workshop_d2_checks={checks} routes={len(routes)} ru={len(ru)} en={len(en)} html={len(html_files)} family_contrast_dark={ratio("#ff9ecb","#2b0a1c"):.2f} family_contrast_panel={ratio("#ff9ecb","#241522"):.2f}')
if errors:
 print('WORKSHOP_D2_FAIL')
 for error in errors:print('-',error)
 sys.exit(1)
print('WORKSHOP_D2_PASS')
