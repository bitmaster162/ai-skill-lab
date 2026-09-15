#!/usr/bin/env python3
from __future__ import annotations
import html,json,re,sys
from html.parser import HTMLParser
from pathlib import Path
from public_origin import PUBLIC_ORIGIN

ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/'deploy'/'live'
ORIGIN=PUBLIC_ORIGIN
ORG_ID=f'{ORIGIN}/#organization'
WEB_ID=f'{ORIGIN}/#website'
PERSON_ID=f'{ORIGIN}/about#person'
TELEGRAM='https://t.me/BiTFormer'
WHATSAPP='https://wa.me/66649701204'
LINE='https://line.me/ti/p/~iwf555'
FORBIDDEN_TYPES={'Review','AggregateRating'}
FORBIDDEN_KEYS={'aggregateRating','review','reviewCount','ratingValue'}
DESCRIPTIONS={
 'ru':'Практическое персональное обучение AI для взрослых, бизнеса, детей и подростков — online worldwide и в Phuket по договорённости.',
 'en':'Practical one-to-one AI education for adults, business, kids and teens — online worldwide and in Phuket by arrangement.',
}

class LDParser(HTMLParser):
 def __init__(self): super().__init__(convert_charrefs=True);self.capture=False;self.buf=[];self.blocks=[]
 def handle_starttag(self,tag,attrs):
  a={k.lower():(v or '') for k,v in attrs}
  if tag=='script' and a.get('type','').lower()=='application/ld+json': self.capture=True;self.buf=[]
 def handle_data(self,data):
  if self.capture:self.buf.append(data)
 def handle_endtag(self,tag):
  if tag=='script' and self.capture:self.blocks.append(''.join(self.buf));self.capture=False;self.buf=[]

def walk(x):
 if isinstance(x,dict):
  yield x
  for v in x.values():yield from walk(v)
 elif isinstance(x,list):
  for v in x:yield from walk(v)

def website():
 return {'@context':'https://schema.org','@type':'WebSite','@id':WEB_ID,'url':ORIGIN,'name':'AI Skill Lab','inLanguage':['ru','en'],'publisher':{'@id':ORG_ID}}

def organization(lang):
 return {'@context':'https://schema.org','@type':'EducationalOrganization','@id':ORG_ID,'name':'AI Skill Lab','url':ORIGIN,'description':DESCRIPTIONS[lang],'email':'robert@aiskillab.work','telephone':'+66649701204','logo':f'{ORIGIN}/og.png','areaServed':[{'@type':'Place','name':'Phuket, Thailand'},{'@type':'Place','name':'Worldwide (online)'}],'founder':{'@id':PERSON_ID},'sameAs':[TELEGRAM,WHATSAPP,LINE]}

def person():
 return {'@context':'https://schema.org','@type':'Person','@id':PERSON_ID,'name':'Dumanyan Robert','jobTitle':'Founder / instructor','worksFor':{'@id':ORG_ID},'url':f'{ORIGIN}/about','email':'robert@aiskillab.work','knowsAbout':['AI systems','Research workflows','AI agents','Automation','Decision workflows','Digital products'],'sameAs':[TELEGRAM]}
def course_list(lang):
 facts=json.loads((ROOT/'data/commercial_facts.json').read_text(encoding='utf-8'))
 en=lang=='en';prefix='/en' if en else '';pricing=prefix+'/pricing';elements=[];position=0
 for track,route in [('adult','personal'),('kids','kids'),('teens','teens')]:
  for plan in facts['tracks'][track]:
   position+=1
   elements.append({'@type':'ListItem','position':position,'item':{'@type':'Course','name':plan['name'],'description':plan['summary_en' if en else 'summary_ru'],'provider':{'@id':ORG_ID},'url':f'{ORIGIN}{prefix}/{route}','inLanguage':lang,'offers':{'@type':'Offer','price':plan['price'].replace('$','').replace(',',''),'priceCurrency':facts['currency'],'category':'Paid','availability':'https://schema.org/InStock','url':f'{ORIGIN}{pricing}'}}})
 return {'@context':'https://schema.org','@type':'ItemList','@id':f'{ORIGIN}{pricing}#courses','name':'AI Skill Lab programs' if en else 'Программы AI Skill Lab','itemListElement':elements}

def visible_faq(path):
 text=path.read_text(encoding='utf-8')
 pairs=[]
 for q,a in re.findall(r'<details[^>]*><summary>(.*?)</summary><p>(.*?)</p></details>',text,re.S):
  clean=lambda s:html.unescape(re.sub(r'<[^>]+>','',s)).strip()
  pairs.append((clean(q),clean(a)))
 return pairs

def faq_page(path,lang):
 route='/en/faq' if lang=='en' else '/faq'
 return {'@context':'https://schema.org','@type':'FAQPage','@id':f'{ORIGIN}{route}#faq','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}} for q,a in visible_faq(path)]}
def main()->int:
 errors=[]
 expected={
  'index.html':[website(),organization('ru')],
  'en.html':[website(),organization('en')],
  'pricing.html':course_list('ru'),
  'en/pricing.html':course_list('en'),
  'faq.html':faq_page(LIVE/'faq.html','ru'),
  'en/faq.html':faq_page(LIVE/'en/faq.html','en'),
  'about.html':person(),
  'en/about.html':person(),
 }
 blocks=0
 for path in sorted(LIVE.rglob('*.html')):
  rel=path.relative_to(LIVE).as_posix();parser=LDParser();parser.feed(path.read_text(encoding='utf-8'))
  want=expected.get(rel)
  if want is None:
   if parser.blocks:errors.append(f'{rel}: JSON-LD not allowed on this route')
   continue
  if len(parser.blocks)!=1:
   errors.append(f'{rel}: expected exactly one JSON-LD block, got {len(parser.blocks)}');continue
  blocks+=1
  try:data=json.loads(parser.blocks[0])
  except Exception as exc:errors.append(f'{rel}: invalid JSON-LD: {exc}');continue
  if data!=want:errors.append(f'{rel}: exact structured-data contract drift')
  for node in walk(data):
   typ=node.get('@type');types={typ} if isinstance(typ,str) else set(typ or []) if isinstance(typ,list) else set()
   if types & FORBIDDEN_TYPES:errors.append(f'{rel}: forbidden schema type {sorted(types & FORBIDDEN_TYPES)}')
   if FORBIDDEN_KEYS & set(node):errors.append(f'{rel}: forbidden rating/review keys {sorted(FORBIDDEN_KEYS & set(node))}')
 for rel in ('faq.html','en/faq.html'):
  if len(visible_faq(LIVE/rel))!=11:errors.append(f'{rel}: visible FAQ count != 11')
 source_checks={
  'app/page.tsx':['<JsonLd data={[websiteSchema, organizationSchemaRu]} />'],
  'app/en/page.tsx':['<JsonLd data={[websiteSchema, organizationSchemaEn]} />'],
  'app/pricing/page.tsx':['<JsonLd data={courseListSchema("ru")} />'],
  'app/en/pricing/page.tsx':['<JsonLd data={courseListSchema("en")} />'],
  'app/faq/page.tsx':['<JsonLd data={faqPageSchema(items, "ru")} />'],
  'app/en/faq/page.tsx':['<JsonLd data={faqPageSchema(items, "en")} />'],
  'app/about/page.tsx':['<JsonLd data={personSchema} />'],
  'app/en/about/page.tsx':['<JsonLd data={personSchema} />'],
 }
 for rel,tokens in source_checks.items():
  text=(ROOT/rel).read_text(encoding='utf-8')
  for token in tokens:
   if token not in text:errors.append(f'{rel}: source parity missing {token}')
 lib=(ROOT/'lib/structured-data.ts').read_text(encoding='utf-8')
 for token in ['courseListSchema','faqPageSchema','personSchema','site.whatsapp','site.line']:
  if token not in lib:errors.append(f'lib/structured-data.ts: missing {token}')
 if 'bitevo.work' in lib:errors.append('lib/structured-data.ts: unverified bitevo.work sameAs forbidden')
 if errors:
  print('STRUCTURED_DATA_FAIL')
  for err in errors:print('-',err)
  return 1
 print(f'STRUCTURED_DATA_PASS routes=8 blocks={blocks} faq_items=22 courses=18 forbidden_claims=0 source_parity=PASS')
 return 0

if __name__=='__main__':raise SystemExit(main())
