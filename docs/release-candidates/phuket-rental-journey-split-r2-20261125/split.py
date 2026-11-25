"""Split rental-journey R2, draft only.
Reuses the exact combined R1 preview (PR #268), moves its tools to separate
noindex pages and leaves a compact gateway inside the existing homes section.
Run: python split.py --repo <checkout> --r1 <R1 candidate dir> --output <new external dir>
No release authority or deploy/live writes. Per-file size check only.
"""
import argparse,hashlib,html,json,subprocess
from html.parser import HTMLParser
from pathlib import Path
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
R1="23c15862d3140266b6c0e307593068f2de141b9f"
RELEASE="AISL_RESTORED_GUIDES_R1_20261122"
PAYLOAD="f11a64758e9c5661eea55a24b9a98c6c078e17dcdfca8e335bd04c23776d99e5"
CSS_SHA="c362ad0aa48033ad465c976619fb0d5a315610baf99e7b8caa2532e18ea6b287"
MAX_HTML=38912 # Historical R7B profile; not authority to change a release.
PINS={
"ru":("phuket-universe.html","2b7c61e013d25815d27b98bb64db9357a64c36a7ec2e6c53a5dfc0ccf357de3a","ed85880e36a6d155f77410808b68e632924630d00de51436a200a1efd59b53f5","3615d7e9daf0ff1a15b80d320ecb4dc4b66c4f31f0eefc576cd1510f5de9223b"),
"en":("en/phuket-universe.html","74f02c92d9595673c289b6dc714a32c8fa099f565fa7272194967fd6befdb9ba","5a68b826edebc1bb0cf08c02a7ccc832180f60e589b12bc009380615bbea9a23","2a37c9bf6010d3fea8c8e8201c1ecc982c14af24f233f45d7f7dfadc352670e6")}
COPY={"ru":("Маршрут арендатора","План поиска, сравнение районов, расходы и вопросы перед просмотром.","Вернуться к жилью","English"),"en":("Rental journey","Search plan, area comparison, costs and viewing questions.","Back to housing","Русский")}
ANCHOR='<section class="pu-s039" id="agencies">'
SECTIONS=["rental-journey","rental-search-plan","area-compare","rental-cost-compare","rental-viewing-checklist"]
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
class Tags(HTMLParser):
 def __init__(self,s):super().__init__(convert_charrefs=True);self.tags=[];self.feed(s);self.close()
 def handle_starttag(self,t,a):self.tags.append((t,dict(a)))
 def handle_startendtag(self,t,a):self.handle_starttag(t,a)
def build(read,r1):
 m=json.loads(read("_release.json"));need(m["release_id"]==RELEASE and m["payload_sha256"]==PAYLOAD,"parent manifest")
 css=read("phuket-universe.css");need(sha(css)==CSS_SHA,"CSS pin")
 output={};report=[]
 for l,(name,pin,combined_pin,calc_pin) in PINS.items():
  raw=read(name);need(sha(raw)==pin,"parent pin")
  combined=(r1/name).read_bytes();need(sha(combined)==combined_pin,"R1 pin")
  old=raw.decode();v=combined.decode();need(old.count(ANCHOR)==1,"agencies anchor")
  before,after=old.split(ANCHOR);suffix=ANCHOR+after
  need(v.startswith(before) and v.endswith(suffix),"R1 insertion boundary")
  tools=v[len(before):-len(suffix)]
  need([a.get("id") for t,a in Tags(tools).tags if t=="section"]==SECTIONS,"R1 sections")
  title,desc,back,lang=COPY[l];e=html.escape
  route="/phuket-universe" if l=="ru" else "/en/phuket-universe"
  guide="preview-tools/"+l+"/rental-journey.html"
  calcpath="preview-tools/"+l+"/rental-budget-calculator.html"
  other="en" if l=="ru" else "ru"
  gateway=f'<div class="pu-s098" id="rental-journey-entry"><p class="pu-s095">{e(desc)}</p><a class="pu-s082" href="/{guide}">{e(title)}</a></div>\n'
  # Insert inside homes, retaining the exact historical four-section order.
  end='</div>\n</section>\n\n'+ANCHOR
  need(old.count(end)==1 and old.index(end)>old.index('id="homes"'),"homes container boundary")
  parent=old.replace(end,gateway+end,1)
  need(parent.replace(gateway,"",1).encode()==raw,"parent preservation")
  pt=Tags(parent).tags
  need([a.get("id") for t,a in pt if t=="section"]==["top","orbit","homes","agencies"],"parent sections")
  need(sum(a.get("id")=="rental-journey-entry" for t,a in pt)==1,"gateway ID")
  need(sum(a.get("href")=="/"+guide for t,a in pt)==1,"gateway link")
  # All previous local #homes destinations now point to the matching aggregator.
  tools=tools.replace('href="#homes"',f'href="{route}#homes"')
  heading='<h2 class="pu-s099" id="rental-journey-title">'
  need(tools.count(heading)==1,"guide heading")
  start=tools.index(heading);finish=tools.index("</h2>",start)
  tools=tools[:start]+tools[start:finish].replace(heading,heading.replace("<h2","<h1"),1)+"</h1>"+tools[finish+5:]
  font='<link rel="preload" href="/fonts/Unbounded-ru-en.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="/fonts/Manrope-latin.woff2" as="font" type="font/woff2" crossorigin>'
  if l=="ru":font+='<link rel="preload" href="/fonts/Manrope-cyrillic.woff2" as="font" type="font/woff2" crossorigin>'
  csp="default-src 'none'; style-src 'self'; font-src 'self'; connect-src 'none'; form-action 'none'; base-uri 'none'; object-src 'none'"
  page=f'<!doctype html><html lang="{l}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta http-equiv="Content-Security-Policy" content="{e(csp,quote=True)}"><title>{e(title)} | Phuket Universe</title>{font}<link rel="stylesheet" href="/phuket-universe.css"></head><body><div class="pu-page" lang="{l}"><header class="pu-s096 pu-pad"><div class="pu-s098"><a class="pu-s082" href="{route}#homes">{e(back)}</a><a class="pu-s082" lang="{other}" href="/preview-tools/{other}/rental-journey.html">{e(lang)}</a></div></header><main id="main">{tools}</main></div></body></html>\n'
  gt=Tags(page).tags;ids=[a["id"] for t,a in gt if "id" in a]
  need(len(ids)==len(set(ids)) and sum(t=="h1" for t,a in gt)==1,"guide IDs/heading")
  need([a.get("id") for t,a in gt if t=="section"]==SECTIONS,"guide sections")
  need(sum(t=="details" for t,a in gt)==5 and sum(t=="input" and a.get("type")=="checkbox" for t,a in gt)==10,"preserve native tools")
  need(not any(t in {"script","form","iframe"} for t,a in gt),"no active submissions")
  need(any(a.get("href")=="/"+calcpath for t,a in gt),"calculator link")
  need(not any(a.get("href")=="#homes" for t,a in gt),"no broken homes links")
  for t,a in gt:
   if a.get("href","").startswith("#"):need(ids.count(a["href"][1:])==1,"local anchor")
  need(sum("data-u2-catalog" in a for t,a in pt)==1 and not any("data-u2-card" in a for t,a in pt),"empty inventory")
  calc=(r1/calcpath).read_bytes();need(sha(calc)==calc_pin,"calculator pin")
  output[name]=parent.encode();output[guide]=page.encode();output[calcpath]=calc
  sizes={name:len(output[name]),guide:len(output[guide]),calcpath:len(calc)}
  need(all(n<=MAX_HTML for n in sizes.values()),"per-file HTML size")
  report.append({"locale":l,"R1_combined_bytes":len(combined),"R2_parent_bytes":sizes[name],"parent_reduction_bytes":len(combined)-sizes[name],"sizes":sizes,"sha256":{k:sha(output[k]) for k in sizes},"historical_cap_bytes":MAX_HTML,"per_file_size":"PASS","structure":"PASS"})
 return output,{"base":BASE,"r1":R1,"scope":"SPLIT_DRAFT_ONLY","pages":report,"release_performance":"NOT_ACCEPTED","limitation":"Historical per-file cap only. Full payload, transfer, route, source parity and successor release gates remain open."}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--repo",required=True,type=Path);p.add_argument("--r1",required=True,type=Path);p.add_argument("--output",required=True,type=Path);a=p.parse_args()
 repo=a.repo.resolve();out=a.output.resolve();git=lambda *v:subprocess.check_output(["git","-C",str(repo),*v])
 need(git("rev-parse",BASE+"^{commit}").decode().strip()==BASE,"Git baseline")
 need(out!=repo and repo not in out.parents and not out.exists(),"new external directory")
 files,report=build(lambda n:git("show",BASE+":deploy/live/"+n),a.r1)
 out.mkdir(parents=True,exist_ok=False)
 for name,raw in files.items():
  f=out/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(raw)
 (out/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
