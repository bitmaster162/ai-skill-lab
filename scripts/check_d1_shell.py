#!/usr/bin/env python3
from __future__ import annotations
from guide_route_admission import admitted_route_count, require_public_html, require_route_set, require_canonical_urls
from pathlib import Path
import json, re, sys

ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/"deploy"/"live"
CSS=LIVE/"workshop.css"
SOURCE=ROOT/"components"/"workshop"/"WorkshopShell.tsx"
SOURCE_CSS=ROOT/"components"/"workshop"/"WorkshopShell.module.css"

LIGHT={"privacy.html","terms.html","en/privacy.html","en/terms.html"}
START={"start.html":"Ответ в течение 1–2 рабочих дней.","en/start.html":"Reply within 1–2 business days."}
CONTACT={
 "ru":{
  "heading":"Как написать",
  "body":"Оставьте заявку или используйте прямой канал; для несовершеннолетнего контакт ведёт взрослый.",
  "reply":"Ответ в течение 1–2 рабочих дней.",
  "start":"/start",
 },
 "en":{
  "heading":"How to reach us",
  "body":"Use the application form or a direct channel; for a minor, coordination stays with an adult.",
  "reply":"Reply within 1–2 business days.",
  "start":"/en/start",
 },
}
CONTACT_URLS=[
 "https://t.me/BiTFormer",
 "https://wa.me/66649701204",
 "https://line.me/ti/p/~iwf555",
 "mailto:robert@aiskillab.work",
]
MENU={
 "ru":["/personal","/teens","/kids","/business","/studio","/pricing"],
 "en":["/en/personal","/en/teens","/en/kids","/en/business","/en/studio","/en/pricing"],
}
FOOTER={
 "ru":["/faq","/about","/challenge","/build","/proof","/method","/curriculum","/phuket"],
 "en":["/en/faq","/en/about","/en/challenge","/en/build","/en/proof","/en/method","/en/curriculum","/en/phuket"],
}
FOOTER_R157={
 "ru":["/faq","/about","/challenge","/build","/proof","/pricing","/start","/kids","/teens","/parents","/personal","/business","/method","/curriculum","/phuket"],
 "en":["/en/faq","/en/about","/en/challenge","/en/build","/en/proof","/en/pricing","/en/start","/en/kids","/en/teens","/en/parents","/en/personal","/en/business","/en/method","/en/curriculum","/en/phuket"],
}
FOOTER_E2={
 "ru":["/faq","/guides","/about","/challenge","/build","/proof","/pricing","/start","/kids","/teens","/parents","/personal","/business","/method","/curriculum","/phuket"],
 "en":["/en/faq","/en/guides","/en/about","/en/challenge","/en/build","/en/proof","/en/pricing","/en/start","/en/kids","/en/teens","/en/parents","/en/personal","/en/business","/en/method","/en/curriculum","/en/phuket"],
}
release=json.loads((LIVE/"_release.json").read_text(encoding="utf-8")).get("release_id")
CAPTION={"ru":"Практический AI · online / Phuket","en":"Practical AI capability · online / Phuket"}

errors=[]; checks=0
def req(ok,msg):
 global checks
 checks+=1
 if not ok: errors.append(msg)

def hrefs(fragment):
 return re.findall(r'<a\b[^>]*href="([^"]+)"',fragment,re.I)

public=[p for p in sorted(LIVE.rglob("*.html")) if p.name!="404.html"]
require_public_html(LIVE)
req(len(public)==admitted_route_count(),f"public pages {len(public)} != {admitted_route_count()}")
reach_count=light_count=start_reply_count=0
for p in public:
 rel=p.relative_to(LIVE).as_posix()
 text=p.read_text(encoding="utf-8")
 lang="en" if rel=="en.html" or rel.startswith("en/") else "ru"
 req(' style=' not in text,f"{rel}: inline style attribute")
 req("fonts.googleapis.com" not in text and "fonts.gstatic.com" not in text,f"{rel}: external font reference")
 header=re.search(r'<header class="workshopHeader">(.*?)</header>',text,re.S)
 req(bool(header),f"{rel}: Workshop header missing")
 if header:
  menu=re.search(r'<nav class="workshopMenu"[^>]*>(.*?)</nav>',header.group(1),re.S)
  req(bool(menu),f"{rel}: Workshop menu missing")
  if menu:req(hrefs(menu.group(1))==MENU[lang],f"{rel}: menu href drift {hrefs(menu.group(1))}")
  req(text.count("data-lab-command-open")==1,f"{rel}: LAB command count")
  req(f'href="{CONTACT[lang]["start"]}"' in header.group(1),f"{rel}: header Start route")
 footer=re.search(r'<footer class="workshopFooter">(.*?)</footer>',text,re.S)
 req(bool(footer),f"{rel}: Workshop footer missing")
 if footer:
  expected_footer=FOOTER_E2[lang] if release in {"E2_GUIDES_R1","N15_AGENT_SAFETY_R1","A4_PHUKET_LOCAL_R1","A3_CALCOM_R1","A5_MENTOR_R1","E1_3_POST_SUBMIT_R1","DESIGN_TYPOGRAPHY_R1","OG20_R1","A7_SAFETY_QUIZ_R1","A8_PROMPT_AUDITOR_R1","A9_REAL_PROJECTS_R1","N25_CERTIFICATE_RECORD_R1","E3_8_LEAD_EVENTS_R1","E3_1_RU_SEO_R1","E3_3_H1_ACTION_R1","E3_2_RU_GLOSSARY_R1","E3_4_AI_SAFETY_AUDIENCE_R1"} else FOOTER_R157[lang] if release in {"R157_I1_3_INDEXABILITY","R158_F1_2_MATCHER_V2","R160_F1_2_PRIVACY_DISCLOSURE"} else FOOTER[lang]
  req(hrefs(footer.group(1))==expected_footer,f"{rel}: footer href drift {hrefs(footer.group(1))}")
  expected_caption = "Практический ИИ · онлайн / Пхукет" if release in {"E3_1_RU_SEO_R1","E3_3_H1_ACTION_R1","E3_2_RU_GLOSSARY_R1","E3_4_AI_SAFETY_AUDIENCE_R1"} and lang == "ru" else CAPTION[lang]
  req(expected_caption in footer.group(1),f"{rel}: footer caption drift")
 reach=re.search(r'<section class="reachBlock">(.*?)</section>',text,re.S)
 if rel in LIGHT:
  req(reach is None,f"{rel}: reach block forbidden")
  req(text.count('class="workshopPage workshopLight"')==1,f"{rel}: light wrapper missing")
  light_count+=1
 elif rel in START:
  req(reach is None,f"{rel}: duplicate reach block")
  req(text.count(START[rel])==1,f"{rel}: reply-time count")
  req('class="workshopPage workshopLight"' not in text,f"{rel}: unexpected light wrapper")
  start_reply_count+=1
 else:
  req(bool(reach),f"{rel}: reach block missing")
  req('class="workshopPage workshopLight"' not in text,f"{rel}: unexpected light wrapper")
  if reach:
   block=reach.group(1); reach_count+=1
   for value in [CONTACT[lang]["heading"],CONTACT[lang]["body"],CONTACT[lang]["reply"]]:
    req(block.count(value)==1,f"{rel}: reach text drift {value!r}")
   links=hrefs(block)
   req(links==[CONTACT[lang]["start"],*CONTACT_URLS],f"{rel}: reach links drift {links}")

req((reach_count,light_count,start_reply_count)==(46,4,2),f"D1 distribution reach/light/start={(reach_count,light_count,start_reply_count)}")

for p in sorted(LIVE.rglob("*.html")):
 req(' style=' not in p.read_text(encoding="utf-8"),f"{p.relative_to(LIVE)}: inline style")

css=CSS.read_text(encoding="utf-8")
source=SOURCE.read_text(encoding="utf-8")
source_css=SOURCE_CSS.read_text(encoding="utf-8")
for name,data in [("static",css),("source",source_css)]:
 compact=data.replace(" ","").replace("\n","")
 for token in ["#0b0d10","#12151a","#171b21","#1d222a","#2a3039","#f5f7f9","#c3cad2","#919aa4","#b9ff3f"]:
  req(token in compact,f"{name}: missing design token {token}")
 req(data.lower().count("#b9ff3f")==1,f"{name}: acid literal count {data.lower().count('#b9ff3f')} != 1")
 req("fonts.googleapis.com" not in data and "fonts.gstatic.com" not in data and "@import" not in data,f"{name}: external CSS/font import")
for marker in [
 '.workshopHeader{min-height:78px',
 '.workshopPrimary{min-height:48px',
 '.reachBlock{margin:0 clamp(18px,3.5vw,44px) 48px',
 '.workshopLight{--g:#f5f7f9',
 '.heroPanel li b{color:var(--i2)}',
 '.workshopPage main .wrap{width:min(1180px,calc(100% - 36px));margin:auto}',
 '.workshopPage main .lesson h2,.workshopPage main .card h2{font-size:clamp(1rem,1.5vw,1.25rem);line-height:1.1;overflow-wrap:anywhere}',
 '.workshopPage main .projectStudioStatus{color:var(--i2)}',
]:
 req(marker in css,f"static CSS missing {marker}")
for marker in [
 '.header{min-height:78px',
 '.primary{min-height:48px',
 '.reachBlock{margin:0 clamp(18px,3.5vw,44px) 48px',
 '.light{--ground:#f5f7f9',
 '.hero h1 em,.startHero h1 em,.pricingHero h1 em,.heroPanel li b,:global(.proofLabTitleRow strong){color:inherit}',
 '.page :global(main .wrap){width:min(1180px,calc(100% - 36px));margin:auto}',
 '.page :global(main .lesson h2),.page :global(main .card h2){font-size:clamp(1rem,1.5vw,1.25rem);line-height:1.1;overflow-wrap:anywhere}',
 '.page :global(main .projectStudioStatus){color:var(--second)}',
]:
 req(marker in source_css,f"source CSS missing {marker}")
for marker in [
 'showReach?: boolean',
 'light?: boolean',
 'showReach ? <ReachBlock locale={locale} /> : null',
 'How to reach us',
 'Как написать',
 'Reply within 1–2 business days.',
 'Ответ в течение 1–2 рабочих дней.',
]:
 req(marker in source,f"source shell missing {marker}")

print(f"d1_shell_checks={checks} public={admitted_route_count()} reach={reach_count} light={light_count} start_reply={start_reply_count}")
if errors:
 print("D1_SHELL_FAIL")
 for error in errors: print("FAIL:",error)
 sys.exit(1)
print("D1_SHELL_PASS")

