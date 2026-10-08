#!/usr/bin/env python3
from pathlib import Path
from html.parser import HTMLParser
import json,re,sys
ROOT=Path(__file__).resolve().parents[1];LIVE=ROOT/"deploy/live";BRAND="AI Skill Lab · Phuket"
RELEASE=json.loads((LIVE/"_release.json").read_text(encoding="utf-8")).get("release_id")
OG20_ALT={
 "/":"Освойте AI так, чтобы результат остался у вас.","/en":"Learn AI so the capability stays with you.",
 "/pricing":"Знайте цену. Фиксируйте scope.","/en/pricing":"Know the price. Define the scope.",
 "/start":"Сначала fit. Потом программа.","/en/start":"Fit first. Program second.",
 "/kids":"AI — не кнопка «сделай за меня».","/en/kids":"AI is not a button that does it for you.",
 "/teens":"Не просто пользоваться AI. Собирать и объяснять.","/en/teens":"Do more than use AI. Build it. Explain it.",
 "/parents":"Платить не за «ребёнок поиграл с AI».","/en/parents":"Do not pay for “my child played with AI.”",
 "/personal":"Не курс про AI, а ваш рабочий процесс.","/en/personal":"Not a course about AI. Your own working system.",
 "/business":"Не «добавить AI». Изменить один процесс.","/en/business":"Do not add AI. Change one process.",
 "/phuket":"Локально на Phuket. И без географии online.","/en/phuket":"Local in Phuket. Borderless online.",
 "/faq":"Одиннадцать ответов до разговора.","/en/faq":"Eleven answers before the call.",
}
GUIDE_TITLES={"/guides/ai-safety-for-kids":"AI и ребёнок 8–13: чек-лист для родителей — AI Skill Lab","/en/guides/ai-safety-for-kids":"AI and your child (8–13): a parent checklist — AI Skill Lab"}
class P(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.lang="";self.title="";self.it=False;self.meta=[];self.links=[]
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=="html":self.lang=d.get("lang","")
  if t=="title":self.it=True
  if t=="meta":self.meta.append(d)
  if t=="link":self.links.append(d)
 def handle_endtag(self,t):
  if t=="title":self.it=False
 def handle_data(self,d):
  if self.it:self.title+=d
def route_for(p):
 rel=p.relative_to(LIVE).as_posix();return "/" if rel=="index.html" else "/en" if rel=="en.html" else "/"+rel[:-5]
errors=[];pages=0;bare=0
for f in sorted(p for p in LIVE.rglob("*.html") if p.name!="404.html"):
 route=route_for(f);en=route=="/en" or route.startswith("/en/");x=P();raw=f.read_text(encoding="utf-8");x.feed(raw);pages+=1
 props={m.get("property"):m.get("content") for m in x.meta if m.get("property")}
 if route in GUIDE_TITLES:
  expected_guide_title = "ИИ и ребёнок 8–13: чек-лист для родителей — AI Skill Lab" if RELEASE in {"E3_1_RU_SEO_R1","E3_3_H1_ACTION_R1"} and route == "/guides/ai-safety-for-kids" else GUIDE_TITLES[route]
  if x.title != expected_guide_title: errors.append(f"{route}: guide title drift")
 elif RELEASE in {"E3_1_RU_SEO_R1","E3_3_H1_ACTION_R1"} and not en:
  if "AI Skill Lab" not in x.title: errors.append(f"{route}: E3.1 RU brand missing")
 elif BRAND not in x.title:errors.append(f"{route}: title brand")
 if props.get("og:site_name")!=BRAND:errors.append(f"{route}: og site name")
 if props.get("og:locale")!=("en_US" if en else "ru_RU"):errors.append(f"{route}: og locale")
 if props.get("og:locale:alternate")!=("ru_RU" if en else "en_US"):errors.append(f"{route}: og alternate")
 expected_alt=OG20_ALT.get(route,BRAND) if RELEASE in {"OG20_R1","A7_SAFETY_QUIZ_R1","A8_PROMPT_AUDITOR_R1","A9_REAL_PROJECTS_R1","N25_CERTIFICATE_RECORD_R1","E3_8_LEAD_EVENTS_R1","E3_1_RU_SEO_R1","E3_3_H1_ACTION_R1"} else BRAND
 if props.get("og:image:alt")!=expected_alt:errors.append(f"{route}: og image alt")
 if (props.get("og:image:width"),props.get("og:image:height"))!=("1200","630"):errors.append(f"{route}: og dimensions")
 alts={a.get("hreflang"):a.get("href") for a in x.links if a.get("rel")=="alternate"}
 if set(alts)!={"ru","en","x-default"}:errors.append(f"{route}: hreflang set")
 for m in re.finditer(r'<a[^>]*href="(?:/en)?/start(?:#[^"]*)?"[^>]*>(.*?)</a>',raw,re.I|re.S):
  label=" ".join(re.sub(r"<[^>]+>"," ",m.group(1)).split())
  if label in {"Start","Начать"}:bare+=1
nf=(LIVE/"404.html").read_text(encoding="utf-8")
if '<html lang="en">' not in nf or "Page not found." not in nf or "/en/start" not in nf:errors.append("404: English contract")
if bare:errors.append(f"bare Start labels={bare}")
print(f"E1_5_METADATA_CHECK pages={pages} bare_start={bare}")
if errors:
 print("E1_5_METADATA_FAIL");[print("-",e) for e in errors];sys.exit(1)
print("E1_5_METADATA_PASS")
