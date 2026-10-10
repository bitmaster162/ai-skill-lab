#!/usr/bin/env python3
from __future__ import annotations
from guide_route_admission import admitted_route_count, require_public_html, require_route_set, require_canonical_urls
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import json,re,sys
from public_origin import PUBLIC_ORIGIN
ROOT=Path(__file__).resolve().parents[1];LIVE=ROOT/'deploy/live';ORIGIN=PUBLIC_ORIGIN
def source_path(rel):
 grouped=(ROOT/'app'/'(ru)'/'layout.tsx').exists() and (ROOT/'app'/'(en)'/'layout.tsx').exists()
 if not grouped or not rel.startswith('app/') or not rel.endswith('page.tsx'):return ROOT/rel
 if rel.startswith('app/en/'):return ROOT/('app/(en)/en/'+rel.removeprefix('app/en/'))
 return ROOT/('app/(ru)/'+rel.removeprefix('app/'))
errors=[];checks=0
CONTACT_URLS=['https://t.me/BiTFormer','https://wa.me/66649701204','https://line.me/ti/p/~iwf555','mailto:robert@aiskillab.work']
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
 text=source_path(rel).read_text(encoding='utf-8')
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
 external=[h for h in a.hrefs if urlparse(h).scheme or h.startswith('//')]
 if external!=CONTACT_URLS:errors.append(f'{rel}: external anchors drift {external}')
 for forbidden in ['href="#"','[response time]','[срок ответа]','x-dc','sc-for','sc-if','support.js','fonts.googleapis.com','fonts.gstatic.com']:
  checks+=1
  if forbidden in text:errors.append(f'{rel}: forbidden {forbidden!r}')
routes={route_for(p) for p in LIVE.rglob('*.html') if p.name!='404.html'}
ru={r for r in routes if r=='/' or not r.startswith('/en')};en={r for r in routes if r=='/en' or r.startswith('/en/')};checks+=5
require_route_set(routes, 'D2 public routes')
if len(routes)!=admitted_route_count():errors.append(f'route authority {len(routes)} != {admitted_route_count()}')
if len(ru)!=admitted_route_count()//2 or len(en)!=admitted_route_count()//2:errors.append(f'locale route authority RU={len(ru)} EN={len(en)}')
if not {'/family','/en/family'}<=routes:errors.append('Family route pair missing')
html_files=list(LIVE.rglob('*.html'))
if len(html_files)!=admitted_route_count()+1:errors.append(f'static HTML count {len(html_files)} != {admitted_route_count()+1}')
sitemap=(LIVE/'sitemap.xml').read_text(encoding='utf-8');locs=set(re.findall(r'<loc>(https?://[^<]+)</loc>',sitemap));expected={ORIGIN+('/' if r=='/' else r) for r in routes};checks+=2
if locs!=expected:errors.append(f'sitemap authority mismatch missing={sorted(expected-locs)} extra={sorted(locs-expected)}')
llms=(LIVE/'llms.txt').read_text(encoding='utf-8');checks+=3
for marker in [f'[RU]({ORIGIN}/family)',f'[EN]({ORIGIN}/en/family)']:
 if marker not in llms:errors.append(f'llms.txt missing {marker}')
require_canonical_urls(re.findall(r'\]\((https?://[^)]+)\)',llms), 'D2 llms links')
readme=(ROOT/'README.md').read_text(encoding='utf-8');checks+=2
for route in ['`/family`','`/en/family`']:
 if readme.count(route)!=1:errors.append(f'README route inventory {route} count={readme.count(route)}')
next_sitemap=(ROOT/'app/sitemap.ts').read_text(encoding='utf-8');checks+=2
for route in ['"/family"','"/en/family"']:
 if next_sitemap.count(route)!=1:errors.append(f'Next sitemap {route} count={next_sitemap.count(route)}')
need('components/workshop/WorkshopHome.tsx',['href={p("/family")}','styles.familyCard'])
need('components/workshop/WorkshopPricing.tsx',['href={p("/family")}','Open Family route','Открыть Family'])
for rel,href in [('deploy/live/index.html','/family'),('deploy/live/en.html','/en/family'),('deploy/live/pricing.html','/family'),('deploy/live/en/pricing.html','/en/family')]:
 text=source_path(rel).read_text(encoding='utf-8');checks+=1
 actual=text.count('href="'+href+'"')
 if actual!=1:errors.append(f'{rel}: Family inbound link count={actual}')
legacy_css=['style.css','style-r68.css','r69-static.css','r77-commercial-mobile.css']
for name in legacy_css:
 checks+=2
 if (LIVE/name).is_file():errors.append(f'retired public CSS still present: {name}')
 if not (ROOT/'archive/legacy-static-css'/name).is_file():errors.append(f'legacy CSS archive missing: {name}')
manifest=json.loads((LIVE/'_release.json').read_text(encoding='utf-8'));checks+=5
if manifest.get('schema')!='ai-skill-lab.static-release.v1':errors.append('release manifest schema drift')
# Current release identity is owned by the D3 release checker.
expected_files=96 if manifest.get('release_id') in {'N25_CERTIFICATE_RECORD_R1','E3_8_LEAD_EVENTS_R1','E3_1_RU_SEO_R1','E3_3_H1_ACTION_R1','E3_2_RU_GLOSSARY_R1','E3_4_AI_SAFETY_AUDIENCE_R1','E3_5_HEADING_STRUCTURE_R1','E3_6_WORKSHOP_HERO_PANEL_R1'} else 94 if manifest.get('release_id') in {'A8_PROMPT_AUDITOR_R1','A9_REAL_PROJECTS_R1'} else 93 if manifest.get('release_id')=='A7_SAFETY_QUIZ_R1' else 92 if manifest.get('release_id')=='OG20_R1' else 72 if manifest.get('release_id') in {'A5_MENTOR_R1','E1_3_POST_SUBMIT_R1','DESIGN_TYPOGRAPHY_R1'} else 71 if manifest.get('release_id') in {'E2_GUIDES_R1','N15_AGENT_SAFETY_R1','A4_PHUKET_LOCAL_R1','A3_CALCOM_R1'} else 67 if manifest.get('release_id') in {'R158_F1_2_MATCHER_V2','R160_F1_2_PRIVACY_DISCLOSURE'} else 66 if manifest.get('release_id') in {'R156_I1_2_INDEXNOW','R157_I1_3_INDEXABILITY'} else 65 if manifest.get('release_id') in {'R145_PWA_INSTALLABILITY','R147_C2_DEPLOYMENT_FILTER_PWA_BACKGROUND','R149_D1_0_WORKSHOP_SHELL','R149_D1_0_VIEWPORT_CLOSEOUT','R151_E1_1_WEB_ANALYTICS','R152_E1_2_CACHE_POLICY','R153_E1_4_INTRO_CALL','R154_E1_5_METADATA','R155_E1_6_MOBILE_HEADER','R156_I1_2_INDEXNOW','R157_I1_3_INDEXABILITY'} else 63 if manifest.get('release_id') in {'R143_R136_A1_A8_CLOSEOUT','R144_ICON_CACHE_PARITY'} else 61 if manifest.get('release_id') in {'R115_WORKSHOP_TYPOGRAPHY','R116_MONETARY_TYPOGRAPHY','R117_GLYPH_FALLBACK','R121_SITEMAP_LASTMOD_REFRESH','R130_STATIC_H2_OVERFLOW_GUARD','R142_A9_A11_FOOTER_TOOLCHAIN_PROOF_TRUTH','R143_R136_A1_A8_CLOSEOUT','R144_ICON_CACHE_PARITY','R145_PWA_INSTALLABILITY','R147_C2_DEPLOYMENT_FILTER_PWA_BACKGROUND','R149_D1_0_WORKSHOP_SHELL','R149_D1_0_VIEWPORT_CLOSEOUT','R151_E1_1_WEB_ANALYTICS','R152_E1_2_CACHE_POLICY','R153_E1_4_INTRO_CALL','R154_E1_5_METADATA','R155_E1_6_MOBILE_HEADER','R156_I1_2_INDEXNOW','R157_I1_3_INDEXABILITY'} else 59 if manifest.get('release_id') in {'R110C_BRAND_LOGO','R111A_NOSCRIPT_FORM_FALLBACK','R111B_BRAND_MARK_FAVICON','R111C_RU_TITLE_LOCALIZATION','R111D_SITEMAP_LASTMOD','R112_PLATFORM_SHORTCUT_TITLES','R114_BRAND_TOUCH_TARGET','R115_WORKSHOP_TYPOGRAPHY','R116_MONETARY_TYPOGRAPHY','R117_GLYPH_FALLBACK','R121_SITEMAP_LASTMOD_REFRESH','R130_STATIC_H2_OVERFLOW_GUARD'} else 58
if manifest.get('file_count')!=expected_files:errors.append(f'manifest file_count {manifest.get("file_count")} != {expected_files}')
listed={x.get('path') for x in manifest.get('files',[])}
if not {'family.html','en/family.html'}<=listed:errors.append('manifest missing Family static pages')
if set(legacy_css)&listed:errors.append('manifest contains retired legacy CSS')
checks+=2
notfound=(LIVE/'404.html').read_text(encoding='utf-8')
if 'href="/workshop.css"' not in notfound or 'href="/style.css"' in notfound:errors.append('404 must use workshop.css only')
if 'noindex,nofollow' not in notfound:errors.append('404 must remain noindex,nofollow')
print(f'workshop_d2_checks={checks} routes={len(routes)} ru={len(ru)} en={len(en)} html={len(html_files)} family_contrast_dark={ratio("#ff9ecb","#2b0a1c"):.2f} family_contrast_panel={ratio("#ff9ecb","#241522"):.2f}')
if errors:
 print('WORKSHOP_D2_FAIL')
 for error in errors:print('-',error)
 sys.exit(1)
print('WORKSHOP_D2_PASS')
