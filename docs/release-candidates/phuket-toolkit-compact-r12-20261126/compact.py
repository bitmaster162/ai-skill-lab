"""R12 compact review candidate from exact R10/R9 bundle.
Run: python compact.py --repo <checkout> --bundle <R10 bundle> --output <new directory>
Deduplicate identical RU/EN CSS/JS; preserve script bytes and inline JSON.
No live payload write, new release admission or performance approval.
"""
import argparse,base64,hashlib,json,re,subprocess,gzip
from html.parser import HTMLParser
from pathlib import Path
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
R10="4b40b89c0c9c533bcd34ee45e8b564ecdcb6743f"
MANIFEST="66c02d9bda23b0424330596b6e74a14576be0259d31f4e1b5a5f8ba07cb251d5"
REVIEW="13a0549668dea88764eecdb20862fb78ea2d5487fed8be2f89857cfadb221bbb"
KINDS={"budget-calculator":1,"shortlist":2,"move-in":1,"move-out":1}
PREFIX="preview-tools/assets/"
def sha(b):return hashlib.sha256(b).hexdigest()
def sri(b):return "sha256-"+base64.b64encode(hashlib.sha256(b).digest()).decode()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def once(s,a,b):
 need(s.count(a)==1,"unique edit boundary")
 return s.replace(a,b,1)
class Tags(HTMLParser):
 def __init__(self,s):super().__init__(convert_charrefs=True);self.tags=[];self.feed(s);self.close()
 def handle_starttag(self,t,a):self.tags.append((t,dict(a)))
 def handle_startendtag(self,t,a):self.handle_starttag(t,a)
def transform(raw,kind):
 old=raw.decode("utf-8");s=old;edits=[];assets={}
 def replace(a,b):
  nonlocal s
  s=once(s,a,b);edits.append((a,b))
 styles=re.findall(r"<style>(.*?)</style>",old,re.S)
 need(len(styles)==1,"one original inline CSS")
 css=styles[0].encode();name=PREFIX+"rental-"+kind+".css";assets[name]=css
 link=f'<link rel="stylesheet" href="/{name}" integrity="{sri(css)}">'
 replace("<style>"+styles[0]+"</style>",link)
 # External stylesheets require self in Chromium; integrity still pins CSS.
 replace("style-src &#x27;"+sri(css)+"&#x27;","style-src &#x27;self&#x27;")
 scripts=re.findall(r"<script>(.*?)</script>",old,re.S)
 need(len(scripts)==KINDS[kind],"script count")
 for i,script in enumerate(scripts,1):
  b=script.encode();name=PREFIX+"rental-"+kind+"-"+str(i)+".js";assets[name]=b
  need(old.count(sri(b))==1,"original CSP script hash")
  replace("<script>"+script+"</script>",f'<script src="/{name}" integrity="{sri(b)}"></script>')
 restored=s
 for a,b in reversed(edits):restored=once(restored,b,a)
 need(restored==old,"preserve every non-edited byte")
 before=Tags(old).tags;after=Tags(s).tags
 need([a for t,a in before if t in {"input","select","textarea","button","a","form"}]==[a for t,a in after if t in {"input","select","textarea","button","a","form"}],"controls and links preserved")
 need(re.findall(r'<script[^>]+type="application/json"[^>]*>.*?</script>',s,re.S)==re.findall(r'<script[^>]+type="application/json"[^>]*>.*?</script>',old,re.S),"locale JSON preserved")
 need(sum(t=="link" and a.get("rel")=="stylesheet" for t,a in after)==1,"one external stylesheet")
 need(sum(t=="script" and "src" in a for t,a in after)==KINDS[kind],"external scripts")
 need(not re.search(r"<script>[\s\S]*?</script>",s),"no inline executable script")
 for t,a in after:
  if (t=="script" and "src" in a) or (t=="link" and a.get("rel")=="stylesheet"):
   n=a.get("src",a.get("href","")).lstrip("/")
   need(n in assets and a.get("integrity")==sri(assets[n]),"resource integrity")
 return s.encode(),assets
def build(parent_raw,bundle):
 need(sha(parent_raw)==MANIFEST,"exact parent manifest")
 m=json.loads(parent_raw);r=(bundle/"REVIEW.json").read_bytes();need(sha(r)==REVIEW,"exact R10 report")
 review=json.loads(r);need(len(review["html"])==12,"12 HTML inputs")
 parent={x["path"]:x for x in m["files"]};old={};out={};shared={}
 for name,v in review["html"].items():
  b=(bundle/"preview"/name).read_bytes();need(sha(b)==v["sha256"] and len(b)==v["bytes"],"input "+name)
  old[name]=b;out[name]=b
 for l in ("ru","en"):
  for kind in KINDS:
   name="preview-tools/"+l+"/rental-"+kind+".html"
   out[name],assets=transform(old[name],kind)
   for a,b in assets.items():
    if a in shared:need(shared[a]==b,"RU/EN resource parity "+a)
    else:shared[a]=b
 need(len(shared)==9,"four CSS, five JS")
 need(not(set(shared)&set(parent)),"asset paths must be new")
 need(len([n for n in old if old[n]!=out[n]])==8,"only eight tool pages")
 need(all(len(b)<=38912 for b in out.values()),"historical HTML cap")
 need(all(len(b)<=41984 for n,b in shared.items() if n.endswith(".css")),"historical CSS cap")
 # No claim of a full deployment; exact projection excludes new manifest and routing policy bytes.
 def projection(files):
  return sum(v["size"] for v in parent.values() if not v["path"].endswith(".woff2"))+sum(len(b)-parent.get(n,{}).get("size",0) for n,b in files.items())
 base=sum(v["size"] for v in parent.values() if not v["path"].endswith(".woff2"))
 orig=projection(old);compact=projection({**out,**shared})
 need(compact<orig and compact>base,"positive measured reduction, new exact admission remains needed")
 def gz(b):return len(gzip.compress(b,compresslevel=9,mtime=0))
 def br(b):
  try:import brotli
  except ImportError:return None
  return len(brotli.compress(b,quality=11))
 rows={n:{"bytes":len(b),"sha256":sha(b),"gzip9_bytes":gz(b),"brotli11_bytes":br(b),"old_bytes":len(old[n]) if n in old else 0} for n,b in {**out,**shared}.items()}
 report={"scope":"COMPACT_DRAFT_ONLY","base":BASE,"r10":R10,"files":rows,"html_changed":8,"html_unchanged":4,"shared_assets":9,"parent_exact_nonfont_bytes":base,"r9_projected_nonfont_bytes":orig,"r12_projected_nonfont_bytes":compact,"saved_bytes":orig-compact,"remaining_delta_bytes":compact-base,"per_html_cap_bytes":38912,"release_approval":False,"limitations":"Exact parent admits only its own measured nonfont payload; new candidate requires separate successor admission. Projected sizes exclude route/profile/manifest changes. Compression is per-file measurement, not production transfer approval. External CSS uses same-origin CSP plus SRI; external JS retains original CSP hashes plus SRI. No live release changes."}
 return {**out,**shared},report
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--repo",required=True,type=Path);p.add_argument("--bundle",required=True,type=Path);p.add_argument("--output",required=True,type=Path);a=p.parse_args()
 repo=a.repo.resolve();out=a.output.resolve();bundle=a.bundle.resolve();git=lambda *v:subprocess.check_output(["git","-C",str(repo),*v])
 need(git("rev-parse",BASE+"^{commit}").decode().strip()==BASE,"Git baseline")
 need(not out.exists() and out!=repo and repo not in out.parents and out!=bundle and bundle not in out.parents,"new external directory")
 files,report=build(git("show",BASE+":deploy/live/_release.json"),bundle)
 out.mkdir(parents=True,exist_ok=False)
 for n,b in files.items():
  f=out/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
 (out/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({k:v for k,v in report.items() if k!="files"},indent=2))
if __name__=="__main__":main()
