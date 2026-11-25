"""R17: measure both exact R16 payloads with pinned gate algorithms.
Read-only audit, not full preflight or release approval.
Run: python audit_static.py --bundle <R16 bundle> --inputs <pinned source files> --output <new folder>
Requires installed Python and Node. No installation, network, or live writes.
"""
import argparse,ast,hashlib,json,subprocess,re,xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,urljoin,unquote
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
REPORT="12dd8ea46e38216d2c8973fee476e768b3db66893a5d4766aefd70e64758c033"
PINS={
"scripts/check_transfer_performance.mjs":"05f1781f24cb7319eea7ffcaea0992eec85964651ada025766ff699b950d791c",
"scripts/check_static_accessibility.py":"39924b267d53bb9816b785a1ae587177b9a2cead6ea195365cfd69b123edebbd",
"scripts/check_static_release.py":"116d4eaf7dfc6ae19f305368421692f4559253ab3c8d4290227a8298c52eb0df",
"scripts/check_security_headers.py":"f0cdc6545a37fa2fd107d5e84ea17a2ae50f3e0c3bc806249466364af52fbfa4",
"data/phuket_universe_u3_e38_r7b_profile.json":"4bb0b241618a3d75aee2de39ffd1771279e4d13399e00af2fa45661e57b26d39"}
PAYLOADS={"parent":"f11a64758e9c5661eea55a24b9a98c6c078e17dcdfca8e335bd04c23776d99e5","static":"fdafd70fc29756d9ebc5c8d05bc9c3ca570189ce9d58b203d3e417f2c006176e"}
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def checked(p,pin):
 b=p.read_bytes();need(sha(b)==pin,"pin "+str(p));return b
def read_payload(p,key):
 files={}
 for f in sorted(p.rglob("*")):
  need(not f.is_symlink(),"symlink")
  if f.is_file():files[f.relative_to(p).as_posix()]=f.read_bytes()
 digest=sha("".join(f"{n}\t{len(b)}\t{sha(b)}\n" for n,b in sorted(files.items())).encode())
 need(digest==PAYLOADS[key] and len(files)==(116 if key=="parent" else 135),"exact payload "+key)
 return files
def source_class(raw,name):
 tree=ast.parse(raw.decode());node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==name)
 ns={"HTMLParser":HTMLParser};exec(compile(ast.Module(body=[node],type_ignores=[]),name+".py","exec"),ns);return ns[name]
def route(n):
 return "/" if n=="index.html" else "/"+n[:-11] if n.endswith("/index.html") else "/"+n[:-5]
class Tags(HTMLParser):
 def __init__(self,b):
  super().__init__(convert_charrefs=True);self.tags=[];self.feed(b.decode());self.close()
 def handle_starttag(self,t,a):self.tags.append((t,dict(a)))
 def handle_startendtag(self,t,a):self.handle_starttag(t,a)
def audit(files,access,pageclass,security):
 pages={n:b for n,b in files.items() if n.endswith(".html")}
 routes={route(n):n for n in pages if Path(n).name!="404.html"}
 parsers={};issues=[];counts=Counter();rows={}
 def check(ok,kind,n,detail):
  counts[kind]+=1
  if not ok:issues.append({"kind":kind,"file":n,"detail":detail})
 config=json.loads(files["vercel.json"])
 csp=next(x["value"] for h in config["headers"] if h["source"]=="/(.*)" for x in h["headers"] if x["key"]=="Content-Security-Policy")
 import base64
 for n,b in pages.items():
  s=b.decode();a=access();a.feed(s);a.close();access_result=a;p=pageclass();p.feed(s);p.close();parsers[n]=p
  t=Tags(b).tags;sec=security();sec.feed(s);sec.close()
  check(a.lang in ("ru","en"),"a11y",n,"language")
  check(a.h1==1,"a11y",n,"one h1")
  check(a.has_main,"a11y",n,"main landmark")
  check(a.has_skip,"a11y",n,"skip link to #main")
  check(len(a.ids)==len(set(a.ids)),"a11y",n,"unique ids")
  for x in a.links:
   check(bool(x["text"].strip() or x["aria"].strip()),"a11y",n,"link name "+x["href"])
   if x["target"]=="_blank":check("noopener" in (x["rel"] or ""),"a11y",n,"noopener "+x["href"])
  for x in a.buttons:
   check(bool(x["text"].strip() or x["aria"].strip()),"a11y",n,"button name")
   if "briefCopy" in x["class"]:check(x["live"]=="polite","a11y",n,"briefCopy live")
  check(" style=" not in s,"security",n,"no inline style attribute")
  for x in sec.s:
   if x.strip():check("'sha256-"+base64.b64encode(hashlib.sha256(x.encode()).digest()).decode()+"'" in csp,"security",n,"inline script hash in global CSP")
  check(len(b)<=38912,"file_size",n,"HTML cap 38912")
  expected=2 if n in ("phuket-universe.html","en/phuket-universe.html") else 1
  styles=[a["href"] for tag,a in t if tag=="link" and a.get("rel")=="stylesheet"]
  check(len(styles)==expected,"stylesheet",n,"stylesheet count")
  for tag,a in t:
   ref=a.get("src") if tag in ("script","img","iframe","source","video","audio") else a.get("href") if tag=="link" and a.get("rel") in ("stylesheet","preload","icon","manifest") else None
   if not ref or ref.startswith("data:") or ref=="/_vercel/insights/script.js":continue
   u=urlsplit(urljoin("https://aiskillab.work/"+n,ref))
   check(u.netloc=="aiskillab.work" and unquote(u.path).lstrip("/") in files,"resource",n,ref)
   if a.get("integrity") and u.path.lstrip("/") in files:
    actual="sha256-"+base64.b64encode(hashlib.sha256(files[u.path.lstrip("/")]).digest()).decode()
    check(actual==a["integrity"],"integrity",n,ref)
  rows[n]={"html_bytes":len(b),"lang":access_result.lang,"skip_link":access_result.has_skip,"stylesheets":styles}
 for n,p in parsers.items():
  if Path(n).name=="404.html":continue
  for href in p.links:
   if href.startswith(("http:","https:","mailto:","tel:","javascript:")):continue
   u=urlsplit(urljoin("https://aiskillab.work"+route(n),href));q=unquote(u.path).rstrip("/") or "/"
   dest=routes.get(q);exists=dest is not None or q.lstrip("/") in files
   check(exists,"link",n,href)
   if dest and u.fragment:check(unquote(u.fragment) in parsers[dest].anchors,"anchor",n,href)
 for n,b in files.items():
  if n.endswith(".css"):check(len(b)<=41984,"file_size",n,"CSS cap 41984")
  if n.endswith(".woff2"):check(len(b)<=55296,"file_size",n,"font cap 55296")
  if Path(n).suffix.lower() in (".png",".jpg",".jpeg",".webp",".gif",".avif"):check(len(b)<=131072,"file_size",n,"image cap 131072")
 return {"checks":dict(counts),"issues":issues,"pages":rows}
def measure(source,root,output):
 # Execute the exact pinned gate's compression and asset-graph functions.
 # Exclude lineage/admission and verdict code: this is measurement only.
 start=source.index("const IMPORT_RE =")
 stop=source.index("const errors = [];",start)
 graph=source[start:stop]
 runner="import fs from 'node:fs';\nimport path from 'node:path';\nimport zlib from 'node:zlib';\nconst LIVE=path.resolve(process.argv[2]);const LIVE_ROOT=LIVE;const LIVE_PREFIX=LIVE+path.sep;\n"+graph+"""
const rows={};const failures=[];
const compressed=new Map();
const cached=(buf,fn)=>{const key=buf.toString("base64")+":"+fn.name;if(!compressed.has(key))compressed.set(key,fn(buf));return compressed.get(key)};
const cachedBr=buf=>cached(buf,br),cachedGz=buf=>cached(buf,gz);
for(const page of walk(LIVE).filter(x=>x.endsWith('.html')).sort()){
 const name=path.relative(LIVE,page).replaceAll('\\\\','/');
 try{
  const buf=fs.readFileSync(page);const {css,js,fonts,documents}=pageAssets(page,buf.toString('utf8'));
  const htmlBr=cachedBr(buf),htmlGz=cachedGz(buf),cssBr=sum(css,cachedBr),cssGz=sum(css,cachedGz),jsBr=sum(js,cachedBr),jsGz=sum(js,cachedGz);
  const fontBytes=fonts.reduce((n,x)=>n+x.buf.length,0);
  const firstBr=htmlBr+cssBr+jsBr+sum(documents,cachedBr),firstGz=htmlGz+cssGz+jsGz+sum(documents,cachedGz);
  rows[name]={htmlBr,htmlGz,cssBr,jsBr,firstBr,firstGz,fontBytes,firstWithFonts:firstBr+fontBytes,fontCount:fonts.length,fonts:fonts.map(x=>path.basename(x.path)).sort()};
 }catch(e){failures.push({file:name,error:String(e.message)})}
}
console.log(JSON.stringify({rows,failures,sharedLabBr:br(fs.readFileSync(path.join(LIVE,'lab-command.js')))}));
"""
 if not output.exists():
  with output.open("x",encoding="utf-8",newline="\n") as f:f.write(runner)
 else:need(output.read_text(encoding="utf-8")==runner,"measurement runner identity")
 r=subprocess.run(["node",str(output),str(root)],capture_output=True,timeout=150,check=True)
 return json.loads(r.stdout)
def compare_metrics(m,profile):
 issues=[]
 for n,r in m["rows"].items():
  p=profile["transfer_profiles"].get(n)
  limits={"htmlBr":10240,"cssBr":p["css_br_max"] if p else 8192,"firstBr":p["first_br_max"] if p else 19456,"firstGz":p["first_gzip_max"] if p else 23040,"fontBytes":p["font_bytes"] if p else 86016,"firstWithFonts":p["first_with_fonts_max"] if p else 102400}
  for k,v in limits.items():
   if r[k]>v:issues.append({"kind":"historical_transfer_comparison","file":n,"detail":k,"observed":r[k],"limit":v})
  want=len(p["fonts"]) if p else 2
  if r["fontCount"]!=want:issues.append({"kind":"historical_font_rule","file":n,"detail":"font preload count","observed":r["fontCount"],"limit":want})
  if p and sorted(p["fonts"])!=r["fonts"]:issues.append({"kind":"historical_font_rule","file":n,"detail":"font preload identity"})
 return issues
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ("bundle","inputs","output"):p.add_argument("--"+n,type=Path,required=True)
 a=p.parse_args();bundle=a.bundle.resolve();inputs=a.inputs.resolve();out=a.output.resolve()
 need(not out.exists() and all(out!=x and x not in out.parents for x in (bundle,inputs)),"new external output")
 m=json.loads(checked(bundle/"MATERIALIZED.json",REPORT));need(not m["release_approval"],"draft")
 src={n:checked(inputs/n,v) for n,v in PINS.items()}
 profile=json.loads(src["data/phuket_universe_u3_e38_r7b_profile.json"])
 ac=source_class(src["scripts/check_static_accessibility.py"],"Audit")
 pc=source_class(src["scripts/check_static_release.py"],"PageParser")
 sc=source_class(src["scripts/check_security_headers.py"],"P")
 files={k:read_payload(bundle/k,k) for k in PAYLOADS}
 out.mkdir(exist_ok=False,parents=True)
 results={}
 for k in PAYLOADS:
  structural=audit(files[k],ac,pc,sc)
  transfer=measure(src["scripts/check_transfer_performance.mjs"].decode(),bundle/k,out/"measure_pinned.mjs")
  results[k]={"structural":structural,"transfer":transfer,"historical_comparisons":compare_metrics(transfer,profile)}
  print(k,len(transfer["rows"]),"pages",sum(structural["checks"].values()),"checks",len(structural["issues"]),"issues",len(transfer["failures"]),"measurement failures",flush=True)
 def issues(k):
  z=results[k];return z["structural"]["issues"]+z["historical_comparisons"]
 key=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
 old={key(x) for x in issues("parent")}
 new=[x for x in issues("static") if key(x) not in old]
 report={"scope":"R17_OWNER_STATIC_DIFFERENTIAL_AUDIT","base":BASE,"r16_report_sha256":REPORT,"source_pins":PINS,"payload_pins":PAYLOADS,"results":results,"new_findings":new,"release_approval":False,"limitations":"Pinned historical transfer algorithms and comparison thresholds, not an admitted successor gate. HTML-level accessibility checks only, no screen reader. Resource check covers selected local attributes. Full preflight, browser/Next runtime and independent review remain open."}
 raw=(json.dumps(report,indent=2,ensure_ascii=False)+"\n").encode()
 with (out/"AUDIT.json").open("xb") as f:f.write(raw)
 print("NEW_FINDINGS",len(new),json.dumps(new,ensure_ascii=False),flush=True)
 print("AUDIT_SHA256",sha(raw),flush=True)
if __name__=="__main__":main()
