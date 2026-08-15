#!/usr/bin/env python3
from __future__ import annotations
import json,re,sys
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/'deploy'/'live'
ORIGIN='https://ai-skill-lab.vercel.app'
ORG_ID=f'{ORIGIN}/#organization'
WEB_ID=f'{ORIGIN}/#website'
TELEGRAM='https://t.me/BiTFormer'
FORBIDDEN_TYPES={'Person','Review','AggregateRating'}
FORBIDDEN_KEYS={'aggregateRating','review','reviewCount','ratingValue','founder','employee','numberOfEmployees'}
DESCRIPTIONS={
 'ru':'Практическое персональное обучение AI для взрослых, бизнеса, детей и подростков — online worldwide и в Phuket по договорённости.',
 'en':'Practical one-to-one AI education for adults, business, kids and teens — online worldwide and in Phuket by arrangement.',
}

class LDParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.capture=False; self.buf=[]; self.blocks=[]
    def handle_starttag(self,tag,attrs):
        a={k.lower():(v or '') for k,v in attrs}
        if tag=='script' and a.get('type','').lower()=='application/ld+json':
            self.capture=True; self.buf=[]
    def handle_data(self,data):
        if self.capture:self.buf.append(data)
    def handle_endtag(self,tag):
        if tag=='script' and self.capture:
            self.blocks.append(''.join(self.buf)); self.capture=False; self.buf=[]

def walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values(): yield from walk(v)
    elif isinstance(x,list):
        for v in x: yield from walk(v)

def check_home(path:Path,lang:str,errors:list[str]):
    p=LDParser(); p.feed(path.read_text(encoding='utf-8'))
    if len(p.blocks)!=1:
        errors.append(f'{path.name}: expected exactly one JSON-LD block, got {len(p.blocks)}'); return 0
    try:data=json.loads(p.blocks[0])
    except Exception as e:
        errors.append(f'{path.name}: invalid JSON-LD: {e}'); return 0
    if not isinstance(data,list) or len(data)!=2:
        errors.append(f'{path.name}: expected [WebSite, EducationalOrganization]'); return 0
    bytype={x.get('@type'):x for x in data if isinstance(x,dict)}
    if set(bytype)!={'WebSite','EducationalOrganization'}:
        errors.append(f'{path.name}: unexpected top-level schema types {sorted(str(x) for x in bytype)}')
        return 0
    web=bytype['WebSite']; org=bytype['EducationalOrganization']
    expected_web={'@context':'https://schema.org','@type':'WebSite','@id':WEB_ID,'url':ORIGIN,'name':'AI Skill Lab','inLanguage':['ru','en'],'publisher':{'@id':ORG_ID}}
    if web!=expected_web: errors.append(f'{path.name}: WebSite schema drift')
    expected_org={'@context':'https://schema.org','@type':'EducationalOrganization','@id':ORG_ID,'name':'AI Skill Lab','url':ORIGIN,'description':DESCRIPTIONS[lang],'sameAs':[TELEGRAM]}
    if org!=expected_org: errors.append(f'{path.name}: EducationalOrganization schema drift for {lang}')
    for node in walk(data):
        t=node.get('@type')
        types={t} if isinstance(t,str) else set(t or []) if isinstance(t,list) else set()
        hit=types & FORBIDDEN_TYPES
        if hit: errors.append(f'{path.name}: forbidden schema type {sorted(hit)}')
        bad=FORBIDDEN_KEYS & set(node)
        if bad: errors.append(f'{path.name}: forbidden unverified schema keys {sorted(bad)}')
    return 1

def main()->int:
    errors=[]; blocks=0
    homes={LIVE/'index.html':'ru',LIVE/'en.html':'en'}
    for p,lang in homes.items(): blocks+=check_home(p,lang,errors)
    for p in sorted(LIVE.rglob('*.html')):
        if p in homes: continue
        parser=LDParser(); parser.feed(p.read_text(encoding='utf-8'))
        if parser.blocks: errors.append(f'{p.relative_to(LIVE)}: JSON-LD must remain home-only for current release')

    ru=(ROOT/'app/page.tsx').read_text(encoding='utf-8')
    en=(ROOT/'app/en/page.tsx').read_text(encoding='utf-8')
    lib=(ROOT/'lib/structured-data.ts').read_text(encoding='utf-8')
    if '<JsonLd data={[websiteSchema, organizationSchemaRu]} />' not in ru:
        errors.append('Next RU home missing structured-data render')
    if '<JsonLd data={[websiteSchema, organizationSchemaEn]} />' not in en:
        errors.append('Next EN home missing structured-data render')
    for token in ['organizationSchemaRu','organizationSchemaEn','publisher: { "@id": `${site.url}/#organization` }']:
        if token not in lib: errors.append(f'Next structured-data source missing {token}')
    if errors:
        print('STRUCTURED_DATA_FAIL')
        for e in errors: print('-',e)
        return 1
    print('STRUCTURED_DATA_PASS homes=2 blocks=2 forbidden_claims=0 source_parity=PASS')
    return 0
if __name__=='__main__': raise SystemExit(main())
