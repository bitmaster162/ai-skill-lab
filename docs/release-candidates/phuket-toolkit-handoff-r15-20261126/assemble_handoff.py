"""R15 combined static + Next review overlay and exact route-policy proposal.
Not a release admission. No writes to the source checkout or historical gates.
Run: python assemble_handoff.py --repo <Git object store> --r13 <R13 candidate>
 --r14 <R14 candidate> --sitemap <exact parent sitemap> --output <new folder>
"""
import argparse,hashlib,json,subprocess,xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path,PurePosixPath
from urllib.parse import urlsplit
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
R13="5c91e6b7eee91a432dc988f38f2e42bfbf6fa00a"
R14="139efe01eb674dda3bf0aac70770a186a5c9f2a7"
MANIFEST="66c02d9bda23b0424330596b6e74a14576be0259d31f4e1b5a5f8ba07cb251d5"
STATIC="cdeb4a954aa77751b6b776419b93f4f9432d70d28d6a66f86fd4d101e21ccc69"
NEXT="b0922405e3741470b449e90e5e0e85681170ce6c7e1f4989161d41fe2d029e8e"
SITEMAP="232305ab57fec5a42fddfcbb02a85c738a7ddef513bfc42b79a7e0d7f36fffbe"
ORIGIN="https://aiskillab.work"
KINDS=("journey","budget-calculator","shortlist","move-in","move-out")
TOOLS=frozenset("/"+("en/" if l=="en" else "")+"phuket-universe/rental-"+k for l in ("ru","en") for k in KINDS)
REPLACEMENTS={"deploy/live/phuket-universe.html","deploy/live/en/phuket-universe.html","components/PhuketUniverse.tsx"}
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def checked(p,pin):
 b=p.read_bytes();need(sha(b)==pin,"pin "+str(p));return b
def pathcheck(n):
 p=PurePosixPath(n)
 need(n==p.as_posix() and not p.is_absolute() and ".." not in p.parts and "\\" not in n and ":" not in n,"unsafe path "+n)
def loadfiles(root,rows):
 out={}
 for n,v in rows.items():
  pathcheck(n);f=root/n
  need(not f.is_symlink() and f.is_file(),"regular file "+n)
  b=checked(f,v["sha256"]);need(len(b)==v["bytes"],"size "+n);out[n]=b
 return out
class Tags(HTMLParser):
 def __init__(self,b):super().__init__(convert_charrefs=True);self.tags=[];self.feed(b.decode());self.close()
 def handle_starttag(self,t,a):self.tags.append((t,dict(a)))
 def handle_startendtag(self,t,a):self.handle_starttag(t,a)
def routes(paths):
 out={}
 for n in paths:
  if not n.endswith(".html") or PurePosixPath(n).name=="404.html":continue
  route="/" if n=="index.html" else "/"+n[:-11] if n.endswith("/index.html") else "/"+n[:-5]
  need(route not in out,"route collision "+route);out[route]=n
 return out
def sitemap_routes(raw):
 root=ET.fromstring(raw);result=[]
 for node in root.findall(".//{*}loc"):
  u=urlsplit(node.text or "")
  need(u.scheme=="https" and u.netloc=="aiskillab.work" and not u.query and not u.fragment,"sitemap origin")
  need(u.path=="/" or not u.path.endswith("/"),"clean sitemap route")
  result.append(u.path)
 need(len(result)==len(set(result)),"duplicate sitemap route")
 return set(result)
def route_policy(parent_paths,projected_paths,documents,sitemap,admitted):
 # Scope is EXACT named candidate, not a generic exemption for noindex.
 # Existing public routes remain a strict equality with the unchanged sitemap.
 base=routes(parent_paths);full=routes(projected_paths);public=sitemap_routes(sitemap)
 need(public==set(base) and len(public)==60,"parent public routes")
 need(set(admitted)==TOOLS and len(admitted)==10,"exact new nonindex route set")
 need(set(full)==public|TOOLS and not(public&TOOLS),"projected route partition")
 need(set(documents)==TOOLS,"exact nonindex document set")
 for route in sorted(TOOLS):
  b=documents[route];need(sha(b)==admitted[route],"nonindex document pin "+route)
  tags=Tags(b).tags
  robots=[a.get("content") for t,a in tags if t=="meta" and a.get("name","").lower()=="robots"]
  need(robots==["noindex,nofollow"],"single exact robots meta "+route)
  need(not any(t=="form" for t,a in tags),"no forms "+route)
  need(not any(t=="script" and not a.get("src") for t,a in tags),"no inline scripts "+route)
  need(sum(t=="link" and a.get("rel")=="stylesheet" for t,a in tags)==1,"one stylesheet "+route)
  need(not any(t=="link" and a.get("rel") in ("canonical","alternate") for t,a in tags),"no public canonical/hreflang "+route)
  need(any(t=="html" and a.get("lang")==("en" if route.startswith("/en/") else "ru") for t,a in tags),"locale "+route)
 return {"public":sorted(public),"nonindex":sorted(TOOLS),"all_html_routes":len(full)}
def build(repo,r13,r14,sitemap):
 def git(*v):return subprocess.check_output(["git","--no-optional-locks","-C",str(repo),*v],timeout=20)
 need(git("rev-parse",BASE+"^{commit}").decode().strip()==BASE,"Git baseline")
 tree={}
 for line in git("ls-tree","-r",BASE).decode().splitlines():
  meta,n=line.split("\t",1);mode,typ,oid=meta.split()
  if typ=="blob":tree[n]=(mode,oid)
 parent_raw=git("show",BASE+":deploy/live/_release.json")
 need(sha(parent_raw)==MANIFEST,"exact parent manifest")
 parent=json.loads(parent_raw);rows={r["path"]:r for r in parent["files"]}
 need(len(rows)==116 and sha(sitemap)==SITEMAP==rows["sitemap.xml"]["sha256"],"parent sitemap")
 a=json.loads(checked(r13/"DRAFT_INVENTORY.json",STATIC))
 b=json.loads(checked(r14/"NEXT_DRAFT.json",NEXT))
 need(a["base"]==b["base"]==BASE and a["status"]=="DRAFT_ONLY_NOT_ADMITTED" and b["scope"]=="NEXT_SOURCE_OVERLAY_DRAFT_ONLY","input scope")
 need(not a["release_approval"] and not b["release_approval"],"not admitted")
 static=loadfiles(r13/"overlay",a["overlay"]);nxt=loadfiles(r14/"overlay",b["files"])
 out={**{"deploy/live/"+n:v for n,v in static.items()},**nxt}
 need(len(static)==21 and len(nxt)==22 and len(out)==43,"43 file overlay")
 need(set(out)&set(tree)==REPLACEMENTS,"exact replacements")
 need(all(tree[n][0]=="100644" for n in REPLACEMENTS),"regular tracked replacements")
 need(not any(n.startswith("scripts/") or n.endswith(("/_release.json","/vercel.json","/sitemap.xml","/robots.txt")) for n in out),"historical gates/metadata untouched")
 projected=dict(rows)
 for n,v in static.items():projected[n]={"path":n,"size":len(v),"sha256":sha(v)}
 inventory=sorted(projected.values(),key=lambda x:x["path"])
 digest=sha("".join(f"{r['path']}\t{r['size']}\t{r['sha256']}\n" for r in inventory).encode())
 need(inventory==a["files"] and digest==a["projected_payload_sha256"],"R13 inventory parity")
 docs={r:static[r[1:]+".html"] for r in TOOLS}
 admitted={r:sha(v) for r,v in docs.items()}
 policy=route_policy(rows,projected,docs,sitemap,admitted)
 need(len(b["routes"])==10 and {r["route"] for r in b["routes"]}==TOOLS,"Next route inventory")
 for r in b["routes"]:
  need(r["body_sha256"]==admitted[r["route"]] and r["static_path"]==r["route"][1:]+".html" and r["handler"] in nxt,"exact cross-renderer pin")
  need(r["headers"]["X-Robots-Tag"]=="noindex, nofollow" and r["headers"]["Cache-Control"]=="no-store","Next headers")
 for n,v in static.items():
  if n.startswith("phuket-rental-assets/"):need(nxt["public/"+n]==v,"shared asset parity "+n)
 need(sha(nxt["public/phuket-universe.css"])==rows["phuket-universe.css"]["sha256"],"guide stylesheet parity")
 delta=[]
 for n,v in sorted(out.items()):
  delta.append({"path":n,"operation":"replace" if n in tree else "add","old_git_blob":tree[n][1] if n in tree else None,"sha256":sha(v),"bytes":len(v)})
 report={"scope":"R15_HANDOFF_DRAFT_ONLY","base":BASE,"r13":R13,"r14":R14,"parent_manifest_sha256":MANIFEST,"route_policy_proposal":policy,"nonindex_document_pins":admitted,"files":delta,"static_payload_projection":{"files":len(inventory),"sha256":digest,"nonfont_bytes":a["projected_nonfont_bytes"]},"release_approval":False,"implementation":"review overlay, not applied","open_gates":["Review and implement a separately versioned exact nonindex-route policy in the real release checker; do not relax historical checks.","Actual Next build/router and full release preflight.","Exact successor admission/manifest lineage, transfer budgets, accessibility, independent review and owner merge."],"limitations":"Parent inventory and pinned Git tree verified; unchanged parent file bytes not all materialized. No actual full-release acceptance."}
 return out,report,rows,projected,docs,admitted
def negative_checks(rows,projected,docs,sitemap,admitted):
 def rejects(f):
  try:f()
  except ValueError:return True
  return False
 r=sorted(TOOLS)[0];bad=dict(docs);bad[r]=bad[r].replace(b"noindex,nofollow",b"index,follow",1)
 badpins={**admitted,r:sha(bad[r])}
 unauthorized="/phuket-universe/rental-extra"
 extra=dict(projected);extra[unauthorized[1:]+".html"]={}
 added=dict(docs);added[unauthorized]=docs[r]
 pins={**admitted,unauthorized:sha(docs[r])}
 sm=ET.fromstring(sitemap)
 ET.SubElement(sm,"{http://www.sitemaps.org/schemas/sitemap/0.9}url").append(ET.Element("{http://www.sitemaps.org/schemas/sitemap/0.9}loc"))
 last=list(sm)[-1];list(last)[0].text=ORIGIN+r
 missing=dict(projected);del missing[r[1:]+".html"]
 return {"indexable_tool_rejected_even_with_new_pin":rejects(lambda:route_policy(rows,projected,bad,sitemap,badpins)),
 "tampered_document_rejected":rejects(lambda:route_policy(rows,projected,bad,sitemap,admitted)),
 "arbitrary_noindex_exception_rejected":rejects(lambda:route_policy(rows,extra,added,sitemap,pins)),
 "missing_tool_rejected":rejects(lambda:route_policy(rows,missing,docs,sitemap,admitted)),
 "sitemap_tool_leak_rejected":rejects(lambda:route_policy(rows,projected,docs,ET.tostring(sm),admitted)),
 "public_route_removal_rejected":rejects(lambda:route_policy(rows,{k:v for k,v in projected.items() if k!="index.html"},docs,sitemap,admitted))}
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ("repo","r13","r14","sitemap","output"):p.add_argument("--"+n,required=True,type=Path)
 a=p.parse_args();out=a.output.resolve();roots=[x.resolve() for x in (a.repo,a.r13,a.r14)]
 need(not out.exists() and all(out!=x and x not in out.parents for x in roots),"new external output")
 sitemap=a.sitemap.read_bytes()
 files,m,rows,projected,docs,pins=build(a.repo,a.r13,a.r14,sitemap)
 checks=negative_checks(rows,projected,docs,sitemap,pins)
 need(all(checks.values()),"negative checks "+str(checks))
 m["negative_checks"]=checks
 out.mkdir(exist_ok=False,parents=True)
 for n,v in files.items():
  f=out/"overlay"/n;f.parent.mkdir(parents=True,exist_ok=True)
  with f.open("xb") as z:z.write(v)
 raw=(json.dumps(m,indent=2,ensure_ascii=False,sort_keys=True)+"\n").encode()
 (out/"HANDOFF.json").write_bytes(raw)
 print("HANDOFF",len(files),"files",len(m["route_policy_proposal"]["public"]),"public",len(m["route_policy_proposal"]["nonindex"]),"noindex","negative",sum(checks.values()),"/",len(checks),"SHA256",sha(raw),flush=True)
if __name__=="__main__":main()
