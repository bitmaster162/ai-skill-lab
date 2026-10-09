#!/usr/bin/env python3
"""E3.4: source-static/locale/bounds proof of learner-focused AI safety for RU personal+teens.
No external network writes, no mutation.
"""
from html.parser import HTMLParser
from pathlib import Path
import hashlib,re,sys
ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/"deploy/live"
import json
release_id=json.loads((LIVE/"_release.json").read_text(encoding="utf-8")).get("release_id")
if release_id != "E3_4_AI_SAFETY_AUDIENCE_R1":
    print("E3_4_AI_SAFETY_NOT_APPLICABLE release="+str(release_id))
    raise SystemExit(0)
PROTECTED={'en/personal.html': 'eb2de9d3b280a9b2f542092b2dba551832cbbcd2f75e1a5e3fa132d502f0c10d', 'en/teens.html': '7643c5b46c066350f5b06d2c0114692138fb1a0905eb16fcb25707f3aa8f5f98', 'business.html': 'c71a4b1176484a8477b9e5f5c97c3fd5e874085acd769164ed039c46f8e9d5e2', 'en/business.html': '31966492f3005b4b9f5f7747b5b75e511978d6e58502cf7a450413dc8f6964fc', 'workshop.css': 'ef8d8e5b453211cd64fad23642397207feca219624b2ab01c9309968fdac06a9'}
OUTSIDE_SECTION={'personal.html': 'a92205dc2d7be3ead54bf2fc13f1d40b2244083e883dae09cf1d7c4ab92b20ee', 'teens.html': '9f83bfe3aa6752a558b359fbb210c55af0e25ead2202575a5e9ab2e01e09cf3e'}
PRICING_SECTION={'personal.html': 'e81fc6ba2abbe91758acb1ed272728d5cb5131ffc9a912613f34095ef0f783c3', 'teens.html': '85c671e2b5391b4506c394e8e153343ac4be87e7e847d5cf7d5a14138130032f'}
SOURCES=(
 "https://replit.com/blog/doubling-down-on-our-commitment-to-secure-vibe-coding",
 "https://www.scworld.com/news/microsoft-365-copilot-zero-click-vulnerability-enabled-data-exfiltration",
 "https://unit42.paloaltonetworks.com/ai-agent-prompt-injection/",
)
HEADINGS=("Не доверять плану. Контролировать эффект.","Полномочия должны быть явными.")
NEW_TITLE="Безопасность ИИ"
BLOCK_RE=re.compile(r'<section class="section agentSafety" id="agent-safety" data-n15-agent-safety="true">([\s\S]*?)</section>')
PRICING_RE=re.compile(r'<section class="section paper" id="pricing">[\s\S]*?</section>')
def digest(b):return hashlib.sha256(b).hexdigest()
errors=[];checks=0
def need(ok,msg):
 global checks
 checks+=1
 if not ok:errors.append(msg)
for rel,expected in PROTECTED.items():
 p=LIVE/rel
 need(p.is_file(),rel+" missing protected asset")
 if p.exists():need(digest(p.read_bytes())==expected,rel+" unrelated byte drift")
source=(ROOT/"components/workshop/AgentSafetyLesson.tsx").read_text(encoding="utf-8")
audience=(ROOT/"components/workshop/WorkshopAudience.tsx").read_text(encoding="utf-8")
builder=(ROOT/"scripts/build_n15_agent_safety.py").read_text(encoding="utf-8")
need('mode?: "standard" | "learner"' in source,"source learner variant type missing")
need('mode === "learner" && locale === "ru"' in source,"source learner mode locale guard missing")
need('mode="learner"' in audience,"audience RU learner mount missing")
need('{audience!=="kids"&&en&&<AgentSafetyLesson locale={locale}/>}' in audience,"EN prepricing legacy safety mount missing")
need('{audience!=="kids"&&!en&&<AgentSafetyLesson locale={locale} mode="learner"/>}' in audience,"RU postpricing safety mount missing")
need("def learner_block() -> str:" in builder,"static builder learner mode missing")
for rel in ("personal.html","teens.html"):
 html=(LIVE/rel).read_text(encoding="utf-8")
 blocks=BLOCK_RE.findall(html)
 need(len(blocks)==1,rel+" one N15 safety section")
 if len(blocks)!=1:continue
 block=blocks[0]
 need(html.count("<h2>"+NEW_TITLE+"</h2>")==1,rel+" exact new H2")
 need(not any(heading in html for heading in HEADINGS),rel+" old business H2 remains")
 need(html.index('id="pricing"')<html.index('id="agent-safety"')<html.index('class="finalCta"'),rel+" safety not after packages")
 need(block.count("<h2>")==1,rel+" safety contains extra H2")
 need(block.count('class="agentSafetyCase"')==3,rel+" case count")
 need(block.count("<li><strong>")==5,rel+" rule count")
 need(block.count('target="_blank" rel="noopener noreferrer"')==3,rel+" hardened sources")
 for url in SOURCES:
  need(block.count('href="'+url+'"')==1,rel+" source link missing "+url)
 need(not any(b in block.lower() for b in ("production","полномоч","control-plane","владельца процесса","бизнес-процесс")),rel+" inappropriate business-authority term")
 combined=BLOCK_RE.sub("",html,count=1)
 need(digest(combined.encode("utf-8"))==OUTSIDE_SECTION[rel],rel+" non-N15 source/static drift")
 prices=PRICING_RE.findall(html)
 need(len(prices)==1,rel+" pricing block count")
 if len(prices)==1:
  need(digest(prices[0].encode("utf-8"))==PRICING_SECTION[rel],rel+" package text/price changed")
for rel in ("en/personal.html","en/teens.html","business.html","en/business.html"):
 html=(LIVE/rel).read_text(encoding="utf-8")
 need(html.count('data-n15-agent-safety="true"')==1,rel+" N15 section count")
 need(NEW_TITLE not in html,rel+" E3.4 locale leaked")
print("E3_4_AI_SAFETY_CHECK checks="+str(checks)+" ru_routes=2 protected_assets=5 sources=3")
if errors:
 print("E3_4_AI_SAFETY_FAIL")
 for e in errors:print("-",e)
 sys.exit(1)
print("E3_4_AI_SAFETY_PASS")
