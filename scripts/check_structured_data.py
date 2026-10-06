#!/usr/bin/env python3
from __future__ import annotations
import html,json,re,sys
from html.parser import HTMLParser
from pathlib import Path
from public_origin import PUBLIC_ORIGIN
ROOT=Path(__file__).resolve().parents[1];LIVE=ROOT/"deploy/live";ORIGIN=PUBLIC_ORIGIN
RELEASE=json.loads((LIVE/"_release.json").read_text(encoding="utf-8")).get("release_id")
ORG_ID=f"{ORIGIN}/#organization";WEB_ID=f"{ORIGIN}/#website";PERSON_ID=f"{ORIGIN}/about#person"
TELEGRAM="https://t.me/BiTFormer";WHATSAPP="https://wa.me/66649701204";LINE="https://line.me/ti/p/~iwf555"
GITHUB="https://github.com/bitmaster162";LINKEDIN="https://www.linkedin.com/in/robert-dumanyan-984171335/";MENTOR_IMAGE=f"{ORIGIN}/robert-dumanyan-mentor.webp"
FORBIDDEN_TYPES={"Review","AggregateRating"};FORBIDDEN_KEYS={"aggregateRating","review","reviewCount","ratingValue"}
DESCRIPTIONS={"ru":"Практическое персональное обучение AI для взрослых, бизнеса, детей и подростков — online worldwide и в Phuket по договорённости.","en":"Practical one-to-one AI education for adults, business, kids and teens — online worldwide and in Phuket by arrangement."}
COURSE={
"ru":{"kids":("AI для детей 8–13","AI для детей 8–13: творчество и собственный проект с участием взрослого, правилами приватности, проверкой результата и безопасной практикой."),"teens":("AI для подростков 14–18","AI для подростков 14–18: research, код, портфолио и собственные проекты с проверкой результата, правилами авторства и контактом через взрослого."),"personal":("Персональное обучение AI","Персональные занятия AI 1-на-1 вокруг реальной задачи: практика, проверяемый проект, разбор инструментов и работа online или на Phuket."),"business":("AI для бизнеса","AI для бизнеса: аудит процессов, обучение команды, bounded pilot, QA и handoff — от выбора задачи до проверяемого результата без лишних обещаний.")},
"en":{"kids":("AI for kids 8–13","AI for kids 8–13: creativity and a learner-owned project with adult coordination, privacy rules, verification and safe practice."),"teens":("AI for teens 14–18","AI for teens 14–18: research, code, portfolio and learner-owned projects with verification, authorship rules and adult coordination."),"personal":("Personal AI learning","One-to-one AI learning around a real task: hands-on practice, a verifiable project, tool review and work online or in Phuket."),"business":("AI for business","Business AI: process audit, team training, bounded pilots, QA and handoff from task selection to a verifiable result without inflated promises.")}}
class LDParser(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.capture=False;self.buf=[];self.blocks=[]
 def handle_starttag(self,t,a):
  d={k.lower():(v or "") for k,v in a}
  if t=="script" and d.get("type","").lower()=="application/ld+json":self.capture=True;self.buf=[]
 def handle_data(self,d):
  if self.capture:self.buf.append(d)
 def handle_endtag(self,t):
  if t=="script" and self.capture:self.blocks.append("".join(self.buf));self.capture=False;self.buf=[]
def walk(x):
 if isinstance(x,dict):
  yield x
  for v in x.values():yield from walk(v)
 elif isinstance(x,list):
  for v in x:yield from walk(v)
def tops(x):return x if isinstance(x,list) else [x]
def organization(lang):
 return {"@context":"https://schema.org","@type":"EducationalOrganization","@id":ORG_ID,"name":"AI Skill Lab","url":ORIGIN,"description":DESCRIPTIONS[lang],"email":"robert@aiskillab.work","telephone":"+66649701204","logo":f"{ORIGIN}/logo.png","areaServed":[{"@type":"Place","name":"Phuket, Thailand"},{"@type":"Place","name":"Worldwide (online)"}],"founder":{"@id":PERSON_ID},"sameAs":[TELEGRAM,WHATSAPP,LINE]}
def website():return {"@context":"https://schema.org","@type":"WebSite","@id":WEB_ID,"url":ORIGIN,"name":"AI Skill Lab","inLanguage":["ru","en"],"publisher":{"@id":ORG_ID}}
def person():
 base={"@context":"https://schema.org","@type":"Person","@id":PERSON_ID,"name":"Dumanyan Robert","jobTitle":"Founder / instructor","worksFor":{"@id":ORG_ID},"url":f"{ORIGIN}/about","email":"robert@aiskillab.work","knowsAbout":["AI systems","Research workflows","AI agents","Automation","Decision workflows","Digital products"],"sameAs":[TELEGRAM]}
 if RELEASE in {"A5_MENTOR_R1","E1_3_POST_SUBMIT_R1","DESIGN_TYPOGRAPHY_R1","OG20_R1","A7_SAFETY_QUIZ_R1","A8_PROMPT_AUDITOR_R1","A9_REAL_PROJECTS_R1","N25_CERTIFICATE_RECORD_R1"}:
  base["name"]="Robert Dumanyan";base["image"]=MENTOR_IMAGE;base["sameAs"]=[TELEGRAM,GITHUB,LINKEDIN]
 return base
def course_page(route,lang):
 name,desc=COURSE[lang][route];prefix="/en" if lang=="en" else ""
 return {"@context":"https://schema.org","@type":"Course","@id":f"{ORIGIN}{prefix}/{route}#course","name":name,"description":desc,"provider":{"@id":ORG_ID},"url":f"{ORIGIN}{prefix}/{route}","inLanguage":lang,"hasCourseInstance":{"@type":"CourseInstance","courseMode":"online","courseWorkload":"PT60M"}}
def course_list(lang):
 facts=json.loads((ROOT/"data/commercial_facts.json").read_text(encoding="utf-8"));en=lang=="en";prefix="/en" if en else "";pricing=prefix+"/pricing";els=[];pos=0
 for track,route in [("adult","personal"),("kids","kids"),("teens","teens")]:
  for plan in facts["tracks"][track]:
   pos+=1;els.append({"@type":"ListItem","position":pos,"item":{"@type":"Course","name":plan["name"],"description":plan["summary_en" if en else "summary_ru"],"provider":{"@id":ORG_ID},"url":f"{ORIGIN}{prefix}/{route}","inLanguage":lang,"offers":{"@type":"Offer","price":plan["price"].replace("$","").replace(",",""),"priceCurrency":facts["currency"],"category":"Paid","availability":"https://schema.org/InStock","url":f"{ORIGIN}{pricing}"}}})
 return {"@context":"https://schema.org","@type":"ItemList","@id":f"{ORIGIN}{pricing}#courses","name":"AI Skill Lab programs" if en else "Программы AI Skill Lab","itemListElement":els}
def visible_faq(p):
 text=p.read_text(encoding="utf-8");pairs=[]
 for q,a in re.findall(r"<details[^>]*><summary>(.*?)</summary><p>(.*?)</p></details>",text,re.S):
  clean=lambda s:html.unescape(re.sub(r"<[^>]+>","",s)).strip();pairs.append((clean(q),clean(a)))
 return pairs
def faq_page(p,lang):
 route="/en/faq" if lang=="en" else "/faq"
 return {"@context":"https://schema.org","@type":"FAQPage","@id":f"{ORIGIN}{route}#faq","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in visible_faq(p)]}
def route_for(p):
 rel=p.relative_to(LIVE).as_posix();return "/" if rel=="index.html" else "/en" if rel=="en.html" else "/"+rel[:-5]
def main():
 errors=[];org_routes=0;course_routes=0;blocks=0;course_items=0
 for p in sorted(LIVE.rglob("*.html")):
  if p.name=="404.html":continue
  route=route_for(p);lang="en" if route=="/en" or route.startswith("/en/") else "ru";parser=LDParser();parser.feed(p.read_text(encoding="utf-8"));blocks+=len(parser.blocks)
  objs=[]
  for raw in parser.blocks:
   try:data=json.loads(raw)
   except Exception as e:errors.append(f"{route}: invalid JSON-LD {e}");continue
   objs.extend(tops(data))
   for node in walk(data):
    typ=node.get("@type");types={typ} if isinstance(typ,str) else set(typ or []) if isinstance(typ,list) else set()
    if types & FORBIDDEN_TYPES:errors.append(f"{route}: forbidden schema type {sorted(types & FORBIDDEN_TYPES)}")
    if FORBIDDEN_KEYS & set(node):errors.append(f"{route}: forbidden rating/review keys")
  orgs=[x for x in objs if x.get("@type")=="EducationalOrganization"]
  if orgs!=[organization(lang)]:errors.append(f"{route}: exact Organization contract drift count={len(orgs)}")
  else:org_routes+=1
  if route in {"/","/en"}:
   if [x for x in objs if x.get("@type")=="WebSite"]!=[website()]:errors.append(f"{route}: WebSite drift")
  if route in {"/about","/en/about"}:
   if [x for x in objs if x.get("@type")=="Person"]!=[person()]:errors.append(f"{route}: Person drift")
  if route in {"/pricing","/en/pricing"}:
   want=course_list(lang);found=[x for x in objs if x.get("@type")=="ItemList"]
   if found!=[want]:errors.append(f"{route}: pricing Course list drift")
   else:course_items+=len(want["itemListElement"])
  if route in {"/faq","/en/faq"}:
   want=faq_page(p,lang);found=[x for x in objs if x.get("@type")=="FAQPage"]
   if found!=[want]:errors.append(f"{route}: FAQPage drift")
  bare=route[4:] if route.startswith("/en/") else route[1:]
  if bare in {"kids","teens","personal","business"}:
   found=[x for x in objs if x.get("@type")=="Course"]
   if found!=[course_page(bare,lang)]:errors.append(f"{route}: Course page drift")
   else:course_routes+=1
 for rel in ("faq.html","en/faq.html"):
  if len(visible_faq(LIVE/rel))!=11:errors.append(f"{rel}: visible FAQ count != 11")
 source_checks={
  "app/(ru)/layout.tsx":["<JsonLd data={organizationSchemaRu} />"],
  "app/(en)/layout.tsx":["<JsonLd data={organizationSchemaEn} />"],
  "app/(ru)/page.tsx":["<JsonLd data={websiteSchema} />"],
  "app/(en)/en/page.tsx":["<JsonLd data={websiteSchema} />"],
  "app/(ru)/faq/page.tsx":['<JsonLd data={faqPageSchema(items, "ru")} />'],
  "app/(en)/en/faq/page.tsx":['<JsonLd data={faqPageSchema(items, "en")} />'],
  "app/(ru)/pricing/page.tsx":['<JsonLd data={courseListSchema("ru")} />'],
  "app/(en)/en/pricing/page.tsx":['<JsonLd data={courseListSchema("en")} />'],
 }
 for route in ("kids","teens","personal","business"):
  source_checks[f"app/(ru)/{route}/page.tsx"]=[f'<JsonLd data={{coursePageSchema("{route}", "ru")}} />']
  source_checks[f"app/(en)/en/{route}/page.tsx"]=[f'<JsonLd data={{coursePageSchema("{route}", "en")}} />']
 for rel,needles in source_checks.items():
  text=(ROOT/rel).read_text(encoding="utf-8")
  for n in needles:
   if n not in text:errors.append(f"{rel}: missing source marker {n}")
 print(f"structured_data_routes=52 blocks={blocks} organization_routes={org_routes} course_routes={course_routes} pricing_courses={course_items} faq_items=22")
 if errors:
  print("STRUCTURED_DATA_FAIL");[print("-",e) for e in errors];return 1
 print("STRUCTURED_DATA_PASS");return 0
if __name__=="__main__":raise SystemExit(main())
