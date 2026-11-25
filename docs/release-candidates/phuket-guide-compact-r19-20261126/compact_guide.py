"""R19 guide-only stylesheet, exact R18 static/Next review candidate.
Run: python compact_guide.py --r18 <candidate> --r14 <candidate> --output <new directory>
Preserves content, controls, font preload identities and original portal resources.
No live writes or release admission.
"""
import argparse,base64,hashlib,json,re,subprocess
from pathlib import Path
from html.parser import HTMLParser
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
R18="2c9641546e4d800cb1f024064e41c1480a0ebc62e328ead60c5ceecb0defece2"
R14="b0922405e3741470b449e90e5e0e85681170ce6c7e1f4989161d41fe2d029e8e"
PAYLOAD="28bd27f39ffd00d57067b99527568df26cbd3fd5a80af13bbf9acea2fc77a3b9"
CSS="c362ad0aa48033ad465c976619fb0d5a315610baf99e7b8caa2532e18ea6b287"
WORKSHOP="a666815eb37b12ab643de504fd17e0a12255d25989c63b364ea5c58693a3da06"
NEW="phuket-rental-assets/rental-journey.css"
PAGES=("phuket-universe/rental-journey.html","en/phuket-universe/rental-journey.html")
CLASSES={"pu-pad","pu-page","pu-s014","pu-s039","pu-s044","pu-s072","pu-s082","pu-s095","pu-s096","pu-s097","pu-s098","pu-s099","pu-s102","pu-s103","pu-s104","pu-s105","pu-s106","pu-skip-link"}
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def sri(b):return "sha256-"+base64.b64encode(hashlib.sha256(b).digest()).decode()
def literal(s):return json.dumps(s,ensure_ascii=False).replace("\u2028","\\u2028").replace("\u2029","\\u2029")
def read(root):
 out={}
 for p in sorted(root.rglob("*")):
  need(not p.is_symlink(),"symlink")
  if p.is_file():out[p.relative_to(root).as_posix()]=p.read_bytes()
 return out
def checked(p,pin):
 b=p.read_bytes();need(sha(b)==pin,"pin "+str(p));return b
def measure(files):
 return {"files":len(files),"payload_sha256":sha("".join(f"{n}\t{len(b)}\t{sha(b)}\n" for n,b in sorted(files.items())).encode()),"total_bytes":sum(map(len,files.values())),"nonfont_bytes":sum(len(b) for n,b in files.items() if not n.endswith(".woff2"))}
def write(root,files):
 for n,b in files.items():
  p=root/n;p.parent.mkdir(exist_ok=True,parents=True)
  with p.open("xb") as f:f.write(b)
class Tags(HTMLParser):
 def __init__(self,s):super().__init__(convert_charrefs=True);self.tags=[];self.feed(s);self.close()
 def handle_starttag(self,t,a):self.tags.append((t,dict(a)))
 def handle_startendtag(self,t,a):self.handle_starttag(t,a)
def derive_css(portal,workshop,docs):
 need(sha(portal)==CSS and sha(workshop)==WORKSHOP,"original stylesheet identity")
 p=portal.decode();w=workshop.decode()
 for doc in docs:
  tags=Tags(doc.decode()).tags
  need({x for t,a in tags for x in a.get("class","").split()}==CLASSES,"exact used class set")
  need(not any(t=="script" or "style" in a for t,a in tags),"native guide")
 font=[x for x in re.findall(r"@font-face\{[^{}]*\}",p) if 'font-family:"Manrope"' in x]
 u=[x for x in re.findall(r"@font-face\{[^{}]*\}",w) if 'font-family:"Unbounded"' in x]
 need(len(font)==2 and len(u)==1,"exact font faces")
 reset="*{box-sizing:border-box;min-width:0}html,body{margin:0;background:#0b0d10;color:#f5f7f9}a{color:inherit;text-decoration:none}h1{overflow-wrap:anywhere}"
 # Preserve the actual portal declarations for all used numbered classes and
 # generic .pu-page selectors. Do not copy unrelated workshop styles.
 rules=[]
 for line in p.splitlines():
  if re.match(r"^\.pu-page \.pu-s[0-9]{3}\{",line):
   cls=re.match(r"^\.pu-page \.(pu-s[0-9]{3})\{",line).group(1)
   if cls in CLASSES:rules.append(line)
  elif line.startswith((".pu-page{",".pu-page *,",".pu-page a{",".pu-page a:hover{",".pu-page :is(a,",".pu-page :is(button,",".pu-page .pu-skip-link{")):rules.append(line)
 need(len(rules)==22,"selected rule inventory "+str(len(rules)))
 need("@import" not in "".join(rules),"no import")
 extra="@media(max-width:720px){.pu-page .pu-pad{padding:40px 24px!important}}\n.pu-page :is(h1,h2,h3,a,label,summary){overflow-wrap:anywhere}.pu-page summary{cursor:pointer}.pu-page summary:focus-visible{outline:3px solid #B9FF3F;outline-offset:4px}.pu-page main:focus-visible{outline:3px solid #39E1C6;outline-offset:-3px}\n"
 result=("\n".join([reset,*font,*u,*rules,extra])).encode()
 need(len(result)<6000 and b"@import" not in result,"bounded standalone stylesheet")
 return result
def build(r18,r14):
 a=json.loads(checked(r18/"R18.json",R18));b=json.loads(checked(r14/"NEXT_DRAFT.json",R14))
 need(a["base"]==b["base"]==BASE and not a["release_approval"] and not b["release_approval"],"draft scope")
 old=read(r18/"static");prior_next=read(r18/"next")
 need(measure(old)["payload_sha256"]==PAYLOAD and len(old)==135,"R18 payload")
 pins={**b["files"],**a["next_delta"]}
 need(set(prior_next)==set(pins),"Next inventory")
 for n,v in pins.items():need(sha(prior_next[n])==v["sha256"] and len(prior_next[n])==v["bytes"],"Next pin "+n)
 need(NEW not in old and "public/"+NEW not in prior_next,"new asset path")
 css=derive_css(old["phuket-universe.css"],old["workshop.css"],[old[n] for n in PAGES])
 new=dict(old);next_new=dict(prior_next);new[NEW]=css;next_new["public/"+NEW]=css
 routes=[]
 for n in PAGES:
  before=old[n].decode();mark='<link rel="stylesheet" href="/phuket-universe.css">'
  replacement='<link rel="stylesheet" href="/'+NEW+'" integrity="'+sri(css)+'">'
  need(before.count(mark)==1,"stylesheet link")
  after=before.replace(mark,replacement,1)
  need(after.replace(replacement,mark,1)==before,"all other HTML bytes preserved")
  new[n]=after.encode()
  row=next(r for r in a["routes"] if r["html_path"]==n)
  handler=row["handler"];s=prior_next[handler].decode();i=s.index("return new Response(")+len("return new Response(")
  body,z=json.JSONDecoder().raw_decode(s[i:])
  need(body.encode()==old[n] and sha(old[n])==row["body_sha256"],"handler preimage")
  next_new[handler]=(s[:i]+literal(after)+s[i+z:]).encode()
  routes.append({**row,"prior_body_sha256":sha(old[n]),"body_sha256":sha(new[n])})
 delta={n for n,v in new.items() if old.get(n)!=v}
 nd={n for n,v in next_new.items() if prior_next.get(n)!=v}
 need(delta==set(PAGES)|{NEW} and nd=={r["handler"] for r in routes}|{"public/"+NEW},"exact delta")
 report={"scope":"R19_GUIDE_CSS_DRAFT_ONLY","base":BASE,"r18_report_sha256":R18,"prior_payload":measure(old),"candidate_payload":measure(new),"static_delta":{n:{"sha256":sha(new[n]),"bytes":len(new[n]),"old_sha256":sha(old[n]) if n in old else None} for n in sorted(delta)},"next_delta":{n:{"sha256":sha(next_new[n]),"bytes":len(next_new[n])} for n in sorted(nd)},"routes":routes,"css_bytes":len(css),"release_approval":False,"limitations":"New standalone guide CSS; prior fonts and preloads retained. Historical font-count/byte discrepancies still require explicit policy. No actual Next build, full visual/accessibility, full preflight, successor admission or independent acceptance."}
 return new,next_new,report
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ("r18","r14","output"):p.add_argument("--"+n,type=Path,required=True)
 a=p.parse_args();out=a.output.resolve();need(not out.exists() and all(out!=x.resolve() and x.resolve() not in out.parents for x in (a.r18,a.r14)),"new external output")
 files,nxt,m=build(a.r18,a.r14);out.mkdir(exist_ok=False,parents=True);write(out/"static",files);write(out/"next",nxt)
 b=(json.dumps(m,ensure_ascii=False,indent=2,sort_keys=True)+"\n").encode();write(out,{"R19.json":b})
 print("BUILT",m["css_bytes"],m["candidate_payload"],"SHA256",sha(b),flush=True)
if __name__=="__main__":main()
