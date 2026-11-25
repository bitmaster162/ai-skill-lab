"""R20 zero-webfont rental tools, review-only successor to exact R19.
Build: python system_fonts.py --r19 <R19 candidate> --r18 <R18 candidate>
 --r14 <R14 candidate> --output <new external dir>
Never writes the checkout or historical admission rules.
"""
import argparse,base64,hashlib,json,re
from pathlib import Path
from html.parser import HTMLParser
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
R19="57bb2559e5f7128f99ab30ae42a194bcec6d9a3e1b94d2cf1c4cbcfbe54c718c"
R18="2c9641546e4d800cb1f024064e41c1480a0ebc62e328ead60c5ceecb0defece2"
R14="b0922405e3741470b449e90e5e0e85681170ce6c7e1f4989161d41fe2d029e8e"
PAYLOAD="bfacc451202a3de1ddb1380d05ee9193492f3fb5abc2d0dbc1ab53774ea23b56"
CSS="phuket-rental-assets/rental-journey.css"
KINDS=("journey","budget-calculator","shortlist","move-in","move-out")
PAGES=tuple(("en/" if l=="en" else "")+"phuket-universe/rental-"+k+".html" for l in ("ru","en") for k in KINDS)
GUIDES=tuple(n for n in PAGES if n.endswith("rental-journey.html"))
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def sri(b):return "sha256-"+base64.b64encode(hashlib.sha256(b).digest()).decode()
def literal(s):return json.dumps(s,ensure_ascii=False).replace("\u2028","\\u2028").replace("\u2029","\\u2029")
def checked(p,pin):
 b=p.read_bytes();need(sha(b)==pin,"pin "+str(p));return b
def read(root):
 out={}
 for p in sorted(root.rglob("*")):
  need(not p.is_symlink(),"symlink "+str(p))
  if p.is_file():out[p.relative_to(root).as_posix()]=p.read_bytes()
 return out
def measure(files):
 return {"files":len(files),"payload_sha256":sha("".join(f"{n}\t{len(b)}\t{sha(b)}\n" for n,b in sorted(files.items())).encode()),"total_bytes":sum(map(len,files.values())),"nonfont_bytes":sum(len(b) for n,b in files.items() if not n.endswith(".woff2"))}
def write(root,files):
 for n,b in files.items():
  p=root/n;p.parent.mkdir(exist_ok=True,parents=True)
  with p.open("xb") as f:f.write(b)
def once(s,a,b):
 need(s.count(a)==1,"unique edit "+a[:90]);return s.replace(a,b,1)
class Tags(HTMLParser):
 def __init__(self,s):
  super().__init__(convert_charrefs=True);self.tags=[];self.feed(s);self.close()
 def handle_starttag(self,t,a):self.tags.append((t,dict(a)))
 def handle_startendtag(self,t,a):self.handle_starttag(t,a)
def font_policy(files,profile):
 """Exact ten route proposal, not a generic exception or production gate."""
 need(set(profile)==set(PAGES),"exact tool set")
 for n in PAGES:
  p=profile[n];raw=files[n];need(sha(raw)==p["html_sha256"],"tool identity "+n)
  tags=Tags(raw.decode()).tags
  styles=[a for t,a in tags if t=="link" and a.get("rel")=="stylesheet"]
  need(len(styles)==1,"single stylesheet")
  a=styles[0];name=a["href"].lstrip("/")
  need(name==p["css_path"] and sha(files[name])==p["css_sha256"] and a.get("integrity")==sri(files[name]),"pinned stylesheet "+n)
  css=files[name].decode()
  need("system-ui" in css and not re.search(r"@font-face|@import|url\s*\(",css,re.I),"no font/CSS imports "+n)
  need(not any(t=="link" and (a.get("as")=="font" or "woff" in a.get("href","")) for t,a in tags),"no font preload "+n)
  need(not any(t=="style" or "style" in a for t,a in tags),"no inline styles")
  csp=[a["content"] for t,a in tags if t=="meta" and a.get("http-equiv","").lower()=="content-security-policy"]
  need(len(csp)==1 and csp[0]==p["csp"],"page CSP identity")
  directives={s.split()[0]:s.split()[1:] for s in csp[0].split(";") if s.strip()}
  need(directives.get("font-src",directives.get("default-src"))==["'none'"],"font network denied")
  need(p["font_count"]==p["font_bytes"]==0,"zero-font budget")
 return True
def build(r19,r18,r14):
 a=json.loads(checked(r19/"R19.json",R19));b=json.loads(checked(r18/"R18.json",R18));c=json.loads(checked(r14/"NEXT_DRAFT.json",R14))
 need(all(x["base"]==BASE and not x["release_approval"] for x in (a,b,c)),"exact draft scope")
 old=read(r19/"static");next_old=read(r19/"next")
 need(measure(old)["payload_sha256"]==PAYLOAD and len(old)==136,"R19 payload")
 pins={**c["files"],**b["next_delta"],**a["next_delta"]}
 need(set(next_old)==set(pins),"Next inventory")
 for n,v in pins.items():need(sha(next_old[n])==v["sha256"] and len(next_old[n])==v["bytes"],"Next pin "+n)
 need(next_old["public/"+CSS]==old[CSS],"shared style")
 css=old[CSS].decode()
 css,n=re.subn(r"@font-face\{[^{}]*\}\r?\n","",css);need(n==3,"three original font faces")
 for original in ('font-family:"Manrope",system-ui,sans-serif','font-family: Unbounded, system-ui, sans-serif'):
  need(css.count(original)==2,"known font declaration")
  css=css.replace(original,"font-family:system-ui,sans-serif")
 need("Manrope" not in css and "Unbounded" not in css,"no webfont dependency")
 new=dict(old);new_next=dict(next_old);new[CSS]=css.encode();new_next["public/"+CSS]=new[CSS]
 routes=[]
 for n in GUIDES:
  row=next(x for x in a["routes"] if x["html_path"]==n)
  s=old[n].decode()
  s,k=re.subn(r'<link rel="preload" href="/fonts/(?:Unbounded-ru-en|Manrope-latin|Manrope-cyrillic)\.woff2" as="font" type="font/woff2" crossorigin>',"",s)
  need(k==(2 if n.startswith("en/") else 3),"known preloads")
  s=once(s,'integrity="'+sri(old[CSS])+'"','integrity="'+sri(new[CSS])+'"')
  s=once(s,"font-src &#x27;self&#x27;","font-src &#x27;none&#x27;")
  # The entire body is unchanged, including skip link, labels and native controls.
  need(s[s.index("<body>"):]==old[n].decode()[old[n].decode().index("<body>"):],"body unchanged")
  new[n]=s.encode()
  handler=row["handler"];source=next_old[handler].decode();i=source.index("return new Response(")+len("return new Response(")
  before,z=json.JSONDecoder().raw_decode(source[i:])
  need(before.encode()==old[n] and sha(old[n])==row["body_sha256"],"prior body")
  tail=once(source[i+z:],"font-src 'self'","font-src 'none'")
  new_next[handler]=(source[:i]+literal(s)+tail).encode()
  headers=dict(row["headers"]);headers["Content-Security-Policy"]=once(headers["Content-Security-Policy"],"font-src 'self'","font-src 'none'")
  routes.append({**row,"headers":headers,"prior_body_sha256":sha(old[n]),"body_sha256":sha(new[n])})
 profile={}
 for n in PAGES:
  tags=Tags(new[n].decode()).tags
  style=next(a["href"].lstrip("/") for t,a in tags if t=="link" and a.get("rel")=="stylesheet")
  csp=next(a["content"] for t,a in tags if t=="meta" and a.get("http-equiv","").lower()=="content-security-policy")
  profile[n]={"html_sha256":sha(new[n]),"css_path":style,"css_sha256":sha(new[style]),"csp":csp,"font_count":0,"font_bytes":0}
 need(font_policy(new,profile),"exact proposed policy")
 sd={n for n in new if new[n]!=old[n]};nd={n for n in new_next if new_next[n]!=next_old[n]}
 need(sd==set(GUIDES)|{CSS} and nd=={x["handler"] for x in routes}|{"public/"+CSS},"exact delta")
 need(measure(new)["files"]==136,"inventory unchanged")
 report={"scope":"R20_SYSTEM_FONT_DRAFT_ONLY","base":BASE,"r19_report_sha256":R19,"prior_payload":measure(old),"candidate_payload":measure(new),"static_delta":{n:{"sha256":sha(new[n]),"bytes":len(new[n]),"old_sha256":sha(old[n])} for n in sorted(sd)},"next_delta":{n:{"sha256":sha(new_next[n]),"bytes":len(new_next[n]),"old_sha256":sha(next_old[n])} for n in sorted(nd)},"routes":routes,"font_policy_proposal":profile,"release_approval":False,"limitations":"Guide typography changes to system-ui (same choice as other tools). Full portal font files and styles untouched. Exact zero-font rule proposed only for these ten pinned tools, not installed in historical checker. Actual Next build, full visual/accessibility, full preflight, successor admission and independent review remain open."}
 return new,new_next,report
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ("r19","r18","r14","output"):p.add_argument("--"+n,type=Path,required=True)
 a=p.parse_args();out=a.output.resolve()
 need(not out.exists() and all(out!=x.resolve() and x.resolve() not in out.parents for x in (a.r19,a.r18,a.r14)),"new external output")
 files,nxt,m=build(a.r19,a.r18,a.r14);out.mkdir(exist_ok=False,parents=True)
 write(out/"static",files);write(out/"next",nxt)
 raw=(json.dumps(m,ensure_ascii=False,indent=2,sort_keys=True)+"\n").encode();write(out,{"R20.json":raw})
 print("R20",len(m["font_policy_proposal"]),"zero-font routes",m["candidate_payload"],"SHA256",sha(raw),flush=True)
if __name__=="__main__":main()
