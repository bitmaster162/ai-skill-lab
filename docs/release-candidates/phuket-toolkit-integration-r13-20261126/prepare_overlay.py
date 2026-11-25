"""R13 clean-route static integration overlay (draft, not deployable).
Run: python prepare_overlay.py --repo <pinned checkout> --candidate <R12>
 --config <exact parent deploy/live/vercel.json> --output <new external dir>
No deploy/live writes, gate exceptions, publication, or successor approval.
"""
import argparse,hashlib,html,json,re,subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
R12="095dcafa61192a75d2082d0d9053d1ff8df287d8"
PARENT="66c02d9bda23b0424330596b6e74a14576be0259d31f4e1b5a5f8ba07cb251d5"
REPORT="ef2ccf408a17f806546e6d358319915686900ad2f896bdab2b5395605d4fe001"
CONFIG="691fa69c52d689ece2ded370065690a72d37ceea648a2952b0fd13db4865773f"
KINDS=("journey","budget-calculator","shortlist","move-in","move-out")
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def checked(path,pin):
 b=path.read_bytes();need(sha(b)==pin,"pin "+str(path));return b
class Audit(HTMLParser):
 def __init__(self,s):
  super().__init__(convert_charrefs=True);self.tags=[];self.feed(s);self.close()
 def handle_starttag(self,t,a):self.tags.append((t,dict(a)))
 def handle_startendtag(self,t,a):self.handle_starttag(t,a)
def path_for(locale,kind):
 return ("en/" if locale=="en" else "")+"phuket-universe/rental-"+kind
def translate(raw,mapping):
 s=raw.decode();before=s
 # Rewrite only actual absolute URL attribute values, not script or JSON contents.
 def attr(m):
  k,q,v=m.groups();return k+q+mapping.get(v,v)+q
 s=re.sub(r'(\b(?:href|src)=)(["\'])([^"\']+)\2',attr,s)
 need("/preview-tools/" not in s,"unmapped preview URL")
 if before!=s:need("preview-tools/" in before,"expected route edits")
 return s
def inert_data(s):
 pattern=r'<script id="(copy|note-copy)" type="application/json">(.*?)</script>'
 matches=re.findall(pattern,s,re.S)
 for key,raw in matches:
  value=json.loads(raw);need(isinstance(value,dict),"locale data object")
  text=html.escape(raw,quote=False)
  old=f'<script id="{key}" type="application/json">{raw}</script>'
  new=f'<div id="{key}" hidden>{text}</div>'
  need(s.count(old)==1 and html.unescape(text)==raw,"exact JSON data preservation")
  s=s.replace(old,new,1)
 return s,len(matches)
def build(parent_raw,config_raw,candidate):
 need(sha(parent_raw)==PARENT,"parent manifest")
 need(sha(config_raw)==CONFIG,"exact parent Vercel config")
 config=json.loads(config_raw)
 need(config["cleanUrls"] is True and config["trailingSlash"] is False,"clean URLs")
 parent=json.loads(parent_raw);rows={x["path"]:x for x in parent["files"]}
 report=json.loads(checked(candidate/"report.json",REPORT))
 need(report["base"]==BASE and len(report["files"])==21,"R12 scope")
 raw={n:checked(candidate/n,v["sha256"]) for n,v in report["files"].items()}
 mapping={};dest={}
 for l in ("ru","en"):
  for k in KINDS:
   old="preview-tools/"+l+"/rental-"+k+".html";new=path_for(l,k)
   mapping["/"+old]="/"+new;dest[old]=new+".html"
 for old in raw:
  if old.startswith("preview-tools/assets/"):
   new="phuket-rental-assets/"+old.split("/")[-1]
   mapping["/"+old]="/"+new;dest[old]=new
 output={};data_count=0
 for name,b in raw.items():
  new=dest.get(name,name)
  if name.endswith(".html"):
   s=translate(b,mapping)
   if name.startswith("preview-tools/"):
    s,n=inert_data(s);data_count+=n
   output[new]=s.encode()
  else:output[new]=b
 need(data_count==6,"six locale data blocks")
 replaced=set(output)&set(rows);added=set(output)-set(rows)
 need(replaced=={"phuket-universe.html","en/phuket-universe.html"} and len(added)==19,"2 replaced / 19 new")
 need(all(n not in rows for n in added),"no collision")
 paths={"/"+n[:-5] for n in output if n.endswith(".html")}
 resources={"/"+n for n in output if not n.endswith(".html")}
 existing_routes={"/"+n[:-5] for n in rows if n.endswith(".html")}
 existing_resources={"/"+n for n in rows}
 audit=[]
 for name,b in output.items():
  if not name.endswith(".html"):continue
  s=b.decode();tags=Audit(s).tags;ids=[a["id"] for t,a in tags if "id" in a]
  need(len(ids)==len(set(ids)),"unique ids "+name)
  need(not any(t=="form" for t,a in tags),"no added forms "+name)
  if name in added:
   need(any(a.get("name")=="robots" and a.get("content")=="noindex,nofollow" for t,a in tags),"noindex")
   need(sum(t=="link" and a.get("rel")=="stylesheet" for t,a in tags)==1,"one stylesheet")
   need(not any(t=="script" and not a.get("src") for t,a in tags),"no inline scripts")
   for t,a in tags:
    if t=="a":
     u=urlsplit(a.get("href",""))
     need(not u.scheme and not u.netloc and (not u.path or u.path in paths|existing_routes),"route "+str(a))
     if not u.path:need(u.fragment in ids,"anchor")
    if (t=="script" and "src" in a) or (t=="link" and a.get("rel") in ("stylesheet","preload")):
     v=a.get("src",a.get("href",""));need(v in resources|existing_resources,"resource "+v)
   audit.append({"route":"/"+name[:-5],"file":name,"robots":"noindex,nofollow","inline_scripts":0,"stylesheet_count":1})
  need(len(b)<=38912,"historical file size")
 # Reconstruct projected full inventory using exact parent rows, without writing any live files.
 projected=dict(rows)
 for n,b in output.items():projected[n]={"path":n,"size":len(b),"sha256":sha(b)}
 inventory=sorted(projected.values(),key=lambda r:r["path"])
 payload=sha("".join(f"{r['path']}\t{r['size']}\t{r['sha256']}\n" for r in inventory).encode())
 old_nonfont=sum(x["size"] for x in rows.values() if not x["path"].endswith(".woff2"))
 nonfont=sum(x["size"] for x in inventory if not x["path"].endswith(".woff2"))
 need(len(inventory)==135 and nonfont>old_nonfont,"successor inventory")
 meta={"schema":"phuket-rental-overlay.draft.v1","status":"DRAFT_ONLY_NOT_ADMITTED","base":BASE,"r12":R12,"parent_manifest_sha256":PARENT,"parent_config_sha256":CONFIG,"projected_file_count":len(inventory),"projected_payload_sha256":payload,"parent_nonfont_bytes":old_nonfont,"projected_nonfont_bytes":nonfont,"delta_nonfont_bytes":nonfont-old_nonfont,"replaced":sorted(replaced),"added":sorted(added),"overlay":{n:{"sha256":sha(b),"bytes":len(b)} for n,b in output.items()},"route_map":audit,"files":inventory,"inert_json_blocks":data_count,"release_approval":False,"open_gates":["New exact successor admission and lineage verifier; parent exact payload does not admit this overlay.","Current check_static_release.py treats every .html as a public sitemap route and requires canonical/hreflang. The ten tools deliberately remain noindex; no sitemap change or exception made.","Next renderer equivalent routes and parent gateway parity are not implemented here.","Full preflight including transfer, accessibility, security and metadata gates not executed. Vercel behavior not deployed/tested."],"scope":"Overlay only; _release.json, vercel.json, sitemap and historical gates are not modified."}
 return output,meta
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--repo",type=Path,required=True);p.add_argument("--candidate",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 repo=a.repo.resolve();candidate=a.candidate.resolve();out=a.output.resolve();git=lambda *v:subprocess.check_output(["git","-C",str(repo),*v])
 need(git("rev-parse",BASE+"^{commit}").decode().strip()==BASE,"verified Git baseline")
 need(not out.exists() and all(out!=x and x not in out.parents for x in (repo,candidate)),"new external output")
 files,meta=build(git("show",BASE+":deploy/live/_release.json"),a.config.read_bytes(),candidate)
 out.mkdir(parents=True,exist_ok=False)
 for n,b in files.items():
  f=out/"overlay"/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
 (out/"DRAFT_INVENTORY.json").write_text(json.dumps(meta,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print(json.dumps({k:v for k,v in meta.items() if k not in ("files","overlay","route_map")},indent=2))
if __name__=="__main__":main()
