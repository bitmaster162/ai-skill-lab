#!/usr/bin/env python3
"""E3.2 exact RU glossary copy, 26-page Latin-count and protected release invariant guard."""
from pathlib import Path
import hashlib,json,sys,re
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/"deploy/live"
EXEMPT=["AI Skill Lab","Proof by Artifact","ChatGPT","Cal.com","Google","Gemini","OpenAI","Microsoft","GitHub","Claude","Anthropic","WhatsApp","Telegram","LINE","Replit","Suno","Python","JavaScript","VS Code","Web","Vercel","Cloudflare","OpenRouter","ROI","API","URL","QA","LLM","SEO","USD","RU","EN","BTC","NVIDIA","Windows","Dumanyan","Robert","Playwright","YouTube","HMAC"]
STOP={"ai","skill","lab","ru","en","api","url","qa","roi","llm","seo","usd","https","www","pdf","kb","mb","json","hmac","v1","v2","v3","ui","ux","mcp","ip"}
W=re.compile(r"(?<![A-Za-z])[A-Za-z][A-Za-z0-9]*(?:[-+][A-Za-z0-9]+)*(?![A-Za-z])")
class Visible(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True);self.body=False;self.stack=[];self.chunks=[]
 def handle_starttag(self,tag,attrs):
  att=dict(attrs)
  if tag=="body":self.body=True
  hidden=tag in {"script","style","noscript","template","svg","head"} or "hidden" in att or att.get("aria-hidden","").lower()=="true" or re.search(r"display\s*:\s*none",att.get("style",""),re.I)!=None or tag=="input" and att.get("type")=="hidden"
  self.stack.append((tag,hidden or (self.stack[-1][1] if self.stack else False)))
 def handle_startendtag(self,tag,attrs):pass
 def handle_endtag(self,tag):
  if tag=="body":self.body=False
  if tag in [x[0] for x in self.stack]:
   while self.stack:
    top=self.stack.pop()
    if top[0]==tag:break
 def handle_data(self,data):
  if self.body and (not self.stack or not self.stack[-1][1]):self.chunks.append(data)
def visible(html):
 p=Visible();p.feed(html);return " ".join(" ".join(p.chunks).split())
def terms(html):
 s=visible(html)
 for b in EXEMPT:s=re.sub(r"(?<![A-Za-z])"+re.escape(b)+r"(?![A-Za-z])"," ",s,flags=re.I)
 return [x.group().lower() for x in W.finditer(s) if x.group().lower() not in STOP]
EXPECTED={'/about': {'before': 64, 'after': 7, 'text_sha256': '9d10bbec9026c02b481ce38b211a38192ce07c3f160d8dde15b1ee37df545594'}, '/build': {'before': 272, 'after': 50, 'text_sha256': '22366161506b4f15ef3781b66a281d05e715977b388895a25055da6b4d25e78f'}, '/business': {'before': 185, 'after': 81, 'text_sha256': '1952d81f3d845b3d79a0250d56a7df8492de195aa71b438bc7fbe9593c3165bb'}, '/certificate': {'before': 54, 'after': 8, 'text_sha256': '88c9239a966d730e059eef328e5943be9c06fa3996e4ceaf496a726899354847'}, '/challenge': {'before': 82, 'after': 22, 'text_sha256': '6c6bd8eab55c0107421745667828373935656cbd4379d80fac8859101701fbf8'}, '/curriculum': {'before': 89, 'after': 10, 'text_sha256': 'b9a768808a5cc6ec8d7bab02e50348e0939315751c658e6f142b1fae0a8f8597'}, '/family': {'before': 23, 'after': 9, 'text_sha256': '305f539d76af0da1fbc7de2f79d925e153584badb275da7a41d6836408a3dcc2'}, '/faq': {'before': 30, 'after': 20, 'text_sha256': 'a8f06e8bfe767d49687256234977bb4c50b1a1bafafde35a59f60c149eed1102'}, '/guides/ai-safety-for-kids': {'before': 78, 'after': 70, 'text_sha256': '8152029ffc5ecad957c829166e3b66e1b8ea9e89621af742272d1b3414d6fa5b'}, '/guides': {'before': 11, 'after': 3, 'text_sha256': '9d6f3bea51580eac7e522d1903f67c8233374022a96fa1bb89eeeb3da2cd9922'}, '/': {'before': 64, 'after': 8, 'text_sha256': '120d2d691e18900cbd876b82afbe3003b4f56566f4c661d8b836e5a9ced59726'}, '/kids': {'before': 34, 'after': 14, 'text_sha256': 'f9b684fe62b982363a34fef9ed019a5f1d97e788e9193cb09bfc111152fb4075'}, '/matcher': {'before': 16, 'after': 3, 'text_sha256': '002b20ac916b73b620800f87653197fba5ec081b140f0b7e5d5e9f896c5f8993'}, '/method': {'before': 21, 'after': 3, 'text_sha256': 'eb6eccffe4c44901354b416a174b9c9afa6d029eda908587e5c707a9af41559d'}, '/parents': {'before': 42, 'after': 12, 'text_sha256': 'c8bf16c2f3a803598527c8ce2a89e71bb820307cda462d2fa263dbcbb55aba06'}, '/personal': {'before': 77, 'after': 52, 'text_sha256': '6ac29f0fab5b16b0488ca596bcfb04161ed54ea0e606b9848142bacb56b6ce64'}, '/phuket': {'before': 31, 'after': 17, 'text_sha256': '5e5daaf2e5a0f9d0a9170aa5ec1073383a355b1bdbc256ec5675e74162abe4a4'}, '/pricing': {'before': 50, 'after': 19, 'text_sha256': 'd4d325a1bbf95b84b72b103a34ab8dbd715d6375bb8e71c55bf619726fe65488'}, '/privacy': {'before': 55, 'after': 47, 'text_sha256': 'b4f048f04db145bf1d97c39765d4c9cbc213ed8c4d0f238f06d06a708c121a6a'}, '/projects': {'before': 376, 'after': 207, 'text_sha256': 'ee6460df5d0c8e1db04cc2b044040c0c005c34a657365fe3a96be133fc77a40a'}, '/proof': {'before': 229, 'after': 58, 'text_sha256': '31a55c0cefc0bfeecef019a50e25a4f8a36fd47fd76bc6bae548a98a971de7d7'}, '/safety': {'before': 26, 'after': 18, 'text_sha256': 'f3f889bcc6c6dd7345a0a4bb91c911e06e323e1aec088a52a18f3854b036f41f'}, '/start': {'before': 39, 'after': 18, 'text_sha256': '7e4e33977a045dd64c23183c56354178ce0e17b15e67186078aa519477c2a2b7'}, '/studio': {'before': 143, 'after': 30, 'text_sha256': 'c30d5bef0228a3da227237b57fff7b2266996c51a87680a3ea82b8a1a51abacd'}, '/teens': {'before': 100, 'after': 57, 'text_sha256': 'c73ac30795c9d7e86bc4154038f5b96ff804efb4b5fe15f21bb839592a4a6fe9'}, '/terms': {'before': 12, 'after': 4, 'text_sha256': '35c3be58676aef8c989cbc375494501a8da2eee70638e51c59cfa353b9471ac1'}}
PROTECTED={'privacy.html': 'e5c30338dc38bffd04f0160760345062080e41edc0a5b2574dedf81aec9207c5', 'terms.html': '6fc8fcbff702491f9e6691d74a7649ccd0511f30544f73bdab0be15dab84f590', 'safety.html': '2329ed2d27a1812f35b9c40179053f4e1d340b3b9352ed0c6b6b9e162c3d4418', 'guides/ai-safety-for-kids.html': 'd4f89748f234aadaf804d721c14b5f39b33f1198a04e71ba0366f8a9722d47ef'}
ENGLISH={'en/about.html': 'e5e7c89ed856beaa84b56e56694b02a78eb37a1abd8934da5ab8cdcfd3950530', 'en/build.html': '6a963b7bacfa0f9eecf57de0299afbff8ed015299f458d2754ab3166ed080c48', 'en/business.html': '31966492f3005b4b9f5f7747b5b75e511978d6e58502cf7a450413dc8f6964fc', 'en/certificate.html': 'e43a3c1c5ca5ceed6c8ead1ec6412a7a363a2a1aa00d9b16451fc02696b7c232', 'en/challenge.html': 'f381308ca6b344ed3785e8168a97768f30353a4c79a668c37b6b5705bfac7f61', 'en/curriculum.html': '7acce68cefdd9cf91f2e72727f202959d8f9db3fb5f19347ca601d91d2326105', 'en/family.html': '52d9880e9356d19c12ecde46d351b746c1d8e9543b5f1f64c230b087d4c11886', 'en/faq.html': '4a880b4aefdeb54d6ffd60bb7d804441c10c95111332b7bbb72e480469a47b62', 'en/guides/ai-safety-for-kids.html': 'a386fd8c652960faf22bf606a00fa0f23afcd26882e424d9d308166a04bd1aaf', 'en/guides.html': 'c6cba5c02a9654eaf60ce61d2e9dfc9a6e0b77e80cce41ab40c6e4a9db1e19b5', 'en/kids.html': '06f7f7f643ba6222df484e68e34bed7611331374d3706a3b7f62876cb56fb3a2', 'en/matcher.html': 'fb2ab78d51a941b87b8cae4d06e8074b9584fecdd8e888d4edc6375591546650', 'en/method.html': '65e3ab868a8f2aa2ebdcde000f3b01cfbc2acfaf17186eac32137e9b935d8617', 'en/parents.html': 'c70ee6601a9395907cc00c51e22acf71252f814e8ebd0fcce84ae58087c3dcdd', 'en/personal.html': 'eb2de9d3b280a9b2f542092b2dba551832cbbcd2f75e1a5e3fa132d502f0c10d', 'en/phuket.html': '10cf9ba9f1dd0b3077b767f5b73080a5c40b75f2ece6d209b77e727afd6f5946', 'en/pricing.html': 'd4c60a15fcc47243f6d3286ce2edfe7b65f7d821d5633bda0210f3447da1e002', 'en/privacy.html': '1273aefe18ed6e938a55bf07776784332108bc794335dcdb12c3862f41ad1141', 'en/projects.html': 'fb7ec221a02b3885e813beb1779b52f1c71fc752b3975801575622adee31e744', 'en/proof.html': '49d525cc0a4ebc268cb4a3d91e880815bd34a21cef5174c5298b46cae11d5353', 'en/safety.html': '7b276e429ff29d322a673f1e22fb611c45cfa6d2a97fd76897c673f9953aa16a', 'en/start.html': 'baae34d9842851d09460189e1161527d39681fbdeffb21512f3f7085bc0e3f28', 'en/studio.html': '15d863d291acb92623f0cd163f0ec50af88bb302fb586447aff7a3439a2ae8e9', 'en/teens.html': '7643c5b46c066350f5b06d2c0114692138fb1a0905eb16fcb25707f3aa8f5f98', 'en/terms.html': 'c0e97aefd66215d012395ec27a8f174bc0c26c9ae0b477d24789cd340e045ec9', 'en.html': '910e3c72f16fd6c5b632236526cced19c6afc572678b8d17febcd70c624fd707'}

RELEASE_ID=json.loads((LIVE/"_release.json").read_text(encoding="utf-8")).get("release_id")
E34_PINS=json.loads((ROOT/"data/e3_4_ru_route_sha_pins.json").read_text(encoding="utf-8"))["routes"] if RELEASE_ID in {"E3_4_AI_SAFETY_AUDIENCE_R1","E3_5_HEADING_STRUCTURE_R1",'E3_6_WORKSHOP_HERO_PANEL_R1'} else {}
E35_PINS=json.loads((ROOT/"data/e3_5_heading_pins.json").read_text(encoding="utf-8")) if RELEASE_ID in {'E3_5_HEADING_STRUCTURE_R1','E3_6_WORKSHOP_HERO_PANEL_R1'} else {}
if E35_PINS:
 assert E35_PINS["release_id"]=="E3_5_HEADING_STRUCTURE_R1"
 ENGLISH=dict(ENGLISH)
 for rel in ("en.html","en/pricing.html"):
  ENGLISH[rel]=E35_PINS["assets"]["deploy/live/"+rel]["accepted_sha256"]
def route_for(rel):
 return "/" if rel=="index.html" else "/"+rel[:-5]
def main():
 errors=[]
 total_before=0;total_after=0
 for route,x in EXPECTED.items():
  rel="index.html" if route=="/" else route.lstrip("/")+".html"
  html=(LIVE/rel).read_text(encoding="utf8")
  text=visible(html)
  seen=hashlib.sha256(text.encode("utf8")).hexdigest()
  n=len(terms(html))
  total_before+=x["before"];total_after+=n
  expected_sha = E35_PINS["routes"][route]["visible_sha256"] if route in E35_PINS.get("routes",{}) else (E34_PINS[route]["visible_sha256"] if route in E34_PINS else x["text_sha256"])
  if seen!=expected_sha:errors.append(f"{route}: exact approved RU visible text SHA drift")
  if n>x["before"]:errors.append(f"{route}: Latin word count increased {n}>{x['before']}")
  if route=="/" and "искусственный интеллект (ИИ) и нейросети" not in text:errors.append("/: canonical opening missing")
  print(f"E3_2_RU route={route} before={x['before']} after={n}")
 if len(EXPECTED)!=26:errors.append(f"route inventory {len(EXPECTED)}")
 if total_after*2>total_before:errors.append(f"Latin reduction below 2x: {total_before}/{total_after}")
 for rel,sha in PROTECTED.items():
  html=(LIVE/rel).read_text(encoding="utf8")
  m=re.search(r"<main\b[^>]*>[\s\S]*?</main>",html)
  if not m or hashlib.sha256(m.group(0).encode("utf8")).hexdigest()!=sha:
   errors.append(f"protected policy/guide main byte drift: {rel}")
 for rel,sha in ENGLISH.items():
  if hashlib.sha256((LIVE/rel).read_bytes()).hexdigest()!=sha:
   errors.append(f"EN static drift: {rel}")
 for route in EXPECTED:
  rel="index.html" if route=="/" else route.lstrip("/")+".html"
  h=(LIVE/rel).read_text(encoding="utf8")
  head=re.search(r"<header\b[^>]*>[\s\S]*?</header>",h)
  if not head:
   errors.append(f"{route}: no header");continue
  if "Ctrl K" in visible(head.group(0)):
   errors.append(f"{route}: visible Ctrl K")
  if 'aria-label="Инструменты"' not in head.group(0):
   errors.append(f"{route}: missing Russian tools label")
  if not re.search(r'<button[^>]*hidden[^>]*data-lab-command-open',head.group(0)):
   errors.append(f"{route}: Ctrl K visual trigger not hidden")
 source=(ROOT/"deploy/live/lab-command.js").read_text(encoding="utf8")
 if "e.key.toLowerCase()==='k'" not in source or "e.metaKey||e.ctrlKey" not in source:
  errors.append("Ctrl+K runtime keyboard handler removed")
 if "asl:lead-event" not in source:errors.append("E3.8 telemetry integration removed")
 print(f"E3_2_GLOSSARY_METRICS routes={len(EXPECTED)} latin_before={total_before} latin_after={total_after} factor={total_before/max(total_after,1):.3f}x english_pages={len(ENGLISH)} protected_pages={len(PROTECTED)}")
 if errors:
  print("E3_2_RU_GLOSSARY_FAIL")
  for err in errors:print("- "+err)
  return 1
 print("E3_2_RU_GLOSSARY_PASS")
 return 0
if __name__=="__main__":
 sys.stdout.reconfigure(encoding="utf8")
 raise SystemExit(main())
