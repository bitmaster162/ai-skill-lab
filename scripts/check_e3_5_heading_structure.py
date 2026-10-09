#!/usr/bin/env python3
"""AI Skill Lab E3.5 P2 exact /pricing and homepage H2 semantics.
Scoped to release E3_5_HEADING_STRUCTURE_R1 only. No mutations/network calls.
"""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/"deploy/live"
RELEASE="E3_5_HEADING_STRUCTURE_R1"
manifest=json.loads((LIVE/"_release.json").read_text(encoding="utf-8"))
if manifest.get("release_id")!=RELEASE:
 print("E3_5_HEADING_NOT_APPLICABLE release="+str(manifest.get("release_id")))
 raise SystemExit(0)
PIN=json.loads((ROOT/"data/e3_5_heading_pins.json").read_text(encoding="utf-8"))
errors=[];checks=0
def need(ok,msg):
 global checks
 checks+=1
 if not ok:errors.append(msg)
def lf(data,rel):
 v=data.replace(b"\r\n",b"\n")
 need(b"\r" not in v and data.count(b"\r\n") in (0,data.count(b"\n")),rel+" malformed EOL")
 return v
def sha(data):return hashlib.sha256(data).hexdigest()
need(PIN.get("schema")=="aiskillab.e3-5.heading-structure.exact-source-pins.v1","schema missing")
need(PIN.get("release_id")==RELEASE,"release id mismatch")
need(PIN.get("base_main")=="6fa0d4d43dabbd56d1b98eb5ffe0fe61a9c3d937","baseline changed")
assets=PIN["assets"]
need(set(assets)=={
"components/workshop/WorkshopPricing.tsx","components/PromptAuditor.tsx","app/globals.css",
"deploy/live/pricing.html","deploy/live/en/pricing.html","deploy/live/index.html",
"deploy/live/en.html","deploy/live/workshop.css"},"asset allowlist mismatch")
for rel,item in assets.items():
 p=ROOT/rel
 need(p.is_file(),rel+" missing")
 if p.is_file():
  data=lf(p.read_bytes(),rel)
  need(sha(data)==item["accepted_sha256"],rel+" exact approved source/content SHA drift")
  need(len(data)==item["accepted_lf_bytes"],rel+" byte-length drift")
for rel,checksum in PIN["preserved"].items():
 p=ROOT/rel
 need(p.is_file(),rel+" original protected asset absent")
 if p.is_file():need(sha(lf(p.read_bytes(),rel))==checksum,rel+" inherited E3.4 or commercial bytes changed")
labels=PIN["age_labels"]
taglines=PIN["tagline"]
for rel,lang in [("deploy/live/pricing.html","ru"),("deploy/live/en/pricing.html","en")]:
 html=(ROOT/rel).read_text(encoding="utf-8")
 h2=[re.sub(r"<[^>]*>","",x).strip() for x in re.findall(r"<h2[^>]*>(.*?)</h2>",html,re.S|re.I)]
 need(len(h2)==10,rel+" expected ten H2 sections")
 need(len(h2)==len(set(h2)),rel+" duplicate H2")
 need(all(h2.count(x)==1 for x in labels[lang]),rel+" group H2 title missing or repeated")
 need(taglines[lang] not in h2,rel+" generic repeated H2 remains")
 need(html.count("<h1")==1,rel+" H1 count changed")
 for label in labels[lang]:
  expected=f'<div class="sectionHead"><span>{taglines[lang]}</span><h2>{label}</h2></div>'
  need(html.count(expected)==1,rel+" semantic heading/eyebrow mismatch "+label)
 need(html.count('class="priceGrid"')==5,rel+" package grids changed")
for rel in ("deploy/live/index.html","deploy/live/en.html"):
 html=(ROOT/rel).read_text(encoding="utf-8")
 vals=[re.sub(r"<[^>]*>","",x).strip() for x in re.findall(r"<h2[^>]*>(.*?)</h2>",html,re.S|re.I)]
 need(len(vals)==8,rel+" H2 count")
 need(all(len(x)>=3 for x in vals),rel+" short H2")
 need(html.count('<p class="promptAuditScore"><span data-pa-score></span>/10</p>')==1,rel+" non-heading score markup missing")
 need(html.count('data-pa-score')==1,rel+" score runtime binding changed")
 need(html.count('src="/prompt-auditor.js"')==1,rel+" auditor runtime script removed")
 need(html.count('data-prompt-auditor')==1,rel+" widget missing")
 need(html.count('<h2><span data-pa-score>')==0,rel+" score still a heading")
source=(ROOT/"components/workshop/WorkshopPricing.tsx").read_text(encoding="utf-8")
need('<h2>{name}</h2>' in source,"React pricing H2 source")
need('><span>{en ? "Choose the depth, not a mystery price." : "Выбирайте глубину, а не неизвестную цену."}</span><h2>{name}</h2>' in source,"React heading mapping")
auditor=(ROOT/"components/PromptAuditor.tsx").read_text(encoding="utf-8")
need('<p className="promptAuditScore">{result.score}/10</p>' in auditor,"React score p")
need('<h2>{result.score}/10</h2>' not in auditor,"React score heading leaked")
need('method: "POST"' in auditor and 'mode: "prompt_audit"' in auditor,"model request behavior drift")
css=(ROOT/"app/globals.css").read_text(encoding="utf-8")
need('.matcherResultTop .promptAuditScore{font-size:clamp(38px,5vw,58px);' in css,"source visual typography")
static=(ROOT/"deploy/live/workshop.css").read_text(encoding="utf-8")
need(static.count(".workshopPage .promptAuditScore{")==2,"static visual typography/wrap")
need(manifest.get("file_count")==96,"static file count must remain 96")
print(f"E3_5_HEADING_CHECK checks={checks} pricing_routes=2 home_routes=2 protected_assets={len(assets)}")
if errors:
 print("E3_5_HEADING_FAIL")
 for err in errors:print("FAIL:",err)
 sys.exit(1)
print("E3_5_HEADING_PASS")
