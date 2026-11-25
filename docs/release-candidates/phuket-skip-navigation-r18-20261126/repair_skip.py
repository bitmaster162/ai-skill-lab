"""R18 native skip navigation for the exact R16 static and R14 Next candidates.
Review only; no live writes, admission, or changes to historical checks.
Run: python repair_skip.py --bundle <R16 bundle> --next <R14 candidate>
 --audit <R17 AUDIT.json> --output <new directory>
"""
import argparse,base64,hashlib,json,re
from pathlib import Path
from html.parser import HTMLParser
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
R16="12dd8ea46e38216d2c8973fee476e768b3db66893a5d4766aefd70e64758c033"
R14="b0922405e3741470b449e90e5e0e85681170ce6c7e1f4989161d41fe2d029e8e"
R17="044f0428c6e3cd04a5fdc8188322e2bee77c58689e8ae4ce219d8d2a9931e9d5"
PAYLOAD="fdafd70fc29756d9ebc5c8d05bc9c3ca570189ce9d58b203d3e417f2c006176e"
KINDS=("journey","budget-calculator","shortlist","move-in","move-out")
TOOLS=("budget-calculator","shortlist","move-in","move-out")
SKIP_CSS="\n.rental-skip-link{position:fixed;left:-10000px;top:12px;z-index:1000;max-width:calc(100% - 24px);padding:12px;background:#B9FF3F;color:#070A12;text-decoration:underline;font-weight:700;overflow-wrap:anywhere}.rental-skip-link:focus{left:12px;outline:3px solid #eef4fc;outline-offset:3px}main#main:focus-visible{outline:3px solid #39e1c6;outline-offset:-3px}\n"
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def sri(b):return "sha256-"+base64.b64encode(hashlib.sha256(b).digest()).decode()
def literal(s):return json.dumps(s,ensure_ascii=False).replace("\u2028","\\u2028").replace("\u2029","\\u2029")
def checked(p,pin):
 b=p.read_bytes();need(sha(b)==pin,"pin "+str(p));return b
def readfiles(root):
 result={}
 for p in sorted(root.rglob("*")):
  need(not p.is_symlink(),"symlink")
  if p.is_file():result[p.relative_to(root).as_posix()]=p.read_bytes()
 return result
def measure(files):
 return {"files":len(files),"payload_sha256":sha("".join(f"{n}\t{len(b)}\t{sha(b)}\n" for n,b in sorted(files.items())).encode()),"total_bytes":sum(map(len,files.values())),"nonfont_bytes":sum(len(b) for n,b in files.items() if not n.endswith(".woff2"))}
def once(s,a,b):
 need(s.count(a)==1,"unique edit "+a[:80]);return s.replace(a,b,1)
class Tags(HTMLParser):
 def __init__(self,s):super().__init__(convert_charrefs=True);self.tags=[];self.feed(s);self.close()
 def handle_starttag(self,t,a):self.tags.append((t,dict(a)))
 def handle_startendtag(self,t,a):self.handle_starttag(t,a)
def path(l,k):return ("en/" if l=="en" else "")+"phuket-universe/rental-"+k+".html"
def css_path(k):return "phuket-rental-assets/rental-"+k+".css"
def fix_html(b,l,k,css_old=None,css_new=None):
 s=b.decode();old=s;label="К основному содержимому" if l=="ru" else "Skip to main content"
 cls="pu-skip-link" if k=="journey" else "rental-skip-link"
 link=f'<a class="{cls}" href="#main">{label}</a>'
 tags=Tags(old).tags
 need(not any(t=="a" and a.get("href")=="#main" and "skip" in a.get("class","") for t,a in tags),"not already fixed")
 if k=="journey":
  marker=f'<body><div class="pu-page" lang="{l}">'
  s=once(s,marker,marker+link);s=once(s,'<main id="main">','<main id="main" tabindex="-1">')
 else:
  s=once(s,"<body>","<body>"+link);s=once(s,"<main>",'<main id="main" tabindex="-1">')
  s=once(s,'integrity="'+sri(css_old)+'"','integrity="'+sri(css_new)+'"')
  if k in ("move-in","move-out"):
   match=re.findall(r'<main id="main" tabindex="-1">(<nav>.*?</nav>)',s,re.S)
   need(len(match)==1,"leading nav")
   nav=match[0];s=once(s,'<main id="main" tabindex="-1">'+nav,'<header class="rental-nav-header">'+nav+'</header><main id="main" tabindex="-1">')
 after=Tags(s).tags
 ids=[a["id"] for t,a in after if "id" in a]
 need(len(ids)==len(set(ids)) and ids.count("main")==1,"main and unique ids")
 need(sum(t=="a" and a.get("href")=="#main" and "skip" in a.get("class","") for t,a in after)==1,"one skip link")
 need([a for t,a in after if t in ("input","select","textarea","button","script")]==[a for t,a in tags if t in ("input","select","textarea","button","script")],"preserve controls/scripts")
 need([a for t,a in after if t=="a" and not(a.get("href")=="#main" and "skip" in a.get("class",""))]==[a for t,a in tags if t=="a"],"preserve links")
 need(len(s.encode())<=38912,"historical HTML cap")
 return s.encode()
def build(bundle,nxt,audit):
 r16=json.loads(checked(bundle/"MATERIALIZED.json",R16));r14=json.loads(checked(nxt/"NEXT_DRAFT.json",R14));r17=json.loads(checked(audit,R17))
 need(r16["base"]==r14["base"]==r17["base"]==BASE,"base identity")
 need(all(not r["release_approval"] for r in (r16,r14,r17)),"draft only")
 before=readfiles(bundle/"static");need(measure(before)["payload_sha256"]==PAYLOAD and len(before)==135,"R16 exact payload")
 wanted={path(l,k) for l in ("ru","en") for k in KINDS}
 findings={x["file"] for x in r17["new_findings"] if x["kind"]=="a11y" and x["detail"]=="skip link to #main"}
 need(findings==wanted,"exact R17 findings")
 next_before=readfiles(nxt/"overlay");need(set(next_before)==set(r14["files"]),"Next overlay inventory")
 for n,v in r14["files"].items():need(sha(next_before[n])==v["sha256"] and len(next_before[n])==v["bytes"],"Next pin "+n)
 after=dict(before);next_after=dict(next_before)
 for k in TOOLS:
  n=css_path(k);old=before[n];need(next_before["public/"+n]==old,"CSS parity")
  extra=SKIP_CSS
  if k in ("move-in","move-out"):
   width=880 if k=="move-in" else 860
   extra+=f".rental-nav-header{{max-width:{width}px;margin:auto;padding:24px 24px 0}}.rental-nav-header+main{{padding-top:0}}\n"
  after[n]=old+extra.encode();next_after["public/"+n]=after[n]
 need(b".pu-page .pu-skip-link:focus{left:12px}" in before["phuket-universe.css"],"existing guide focus style")
 route_rows=[]
 for l in ("ru","en"):
  for k in KINDS:
   n=path(l,k)
   css=css_path(k)
   after[n]=fix_html(before[n],l,k,before.get(css),after.get(css))
   row=next(x for x in r14["routes"] if x["static_path"]==n)
   handler=row["handler"];source=next_before[handler].decode()
   mark="return new Response(";i=source.index(mark)+len(mark)
   old_body,end=json.JSONDecoder().raw_decode(source[i:])
   need(old_body.encode()==before[n] and sha(before[n])==row["body_sha256"],"original handler parity")
   next_after[handler]=(source[:i]+literal(after[n].decode())+source[i+end:]).encode()
   route_rows.append({**row,"body_sha256":sha(after[n]),"prior_body_sha256":sha(before[n]),"html_path":n})
 changed={n for n in after if after[n]!=before[n]}
 changed_next={n for n in next_after if next_after[n]!=next_before[n]}
 need(changed==wanted|{css_path(k) for k in TOOLS} and len(changed)==14,"static exact delta")
 need(len(changed_next)==14 and len(next_after)==22,"Next exact delta")
 need(all(after[n]==before[n] for n in before if n not in changed),"unchanged bytes")
 meta={"scope":"R18_SKIP_NAVIGATION_DRAFT_ONLY","base":BASE,"prior_payload":measure(before),"candidate_payload":measure(after),"fixed_findings":sorted(findings),"static_delta":{n:{"sha256":sha(after[n]),"old_sha256":sha(before[n]),"bytes":len(after[n])} for n in sorted(changed)},"next_delta":{n:{"sha256":sha(next_after[n]),"old_sha256":sha(next_before[n]),"bytes":len(next_after[n])} for n in sorted(changed_next)},"routes":route_rows,"release_approval":False,"limitations":"Ten skip-navigation fixes. Historical font/transfer comparisons, full accessibility, actual Next build/router, full preflight, admission and independent review remain open."}
 return after,next_after,meta
def write(root,files):
 for n,b in files.items():
  f=root/n;f.parent.mkdir(parents=True,exist_ok=True)
  with f.open("xb") as z:z.write(b)
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ("bundle","next","audit","output"):p.add_argument("--"+n,type=Path,required=True)
 a=p.parse_args();out=a.output.resolve()
 need(not out.exists() and all(out!=x.resolve() and x.resolve() not in out.parents for x in (a.bundle,a.next,a.audit.parent)),"new external output")
 files,nxt,m=build(a.bundle,a.next,a.audit)
 out.mkdir(parents=True,exist_ok=False);write(out/"static",files);write(out/"next",nxt)
 raw=(json.dumps(m,indent=2,ensure_ascii=False,sort_keys=True)+"\n").encode();write(out,{"R18.json":raw})
 print("R18",len(m["fixed_findings"]),"fixes",len(m["static_delta"]),"static",len(m["next_delta"]),"Next",m["candidate_payload"],"SHA256",sha(raw),flush=True)
if __name__=="__main__":main()
