"""R14 Next source overlay for exact R13 rental documents.
Review only: no checkout edits, install, build, release, or deployment.
Run: python prepare_next.py --repo <pinned Git checkout> --r13 <R13 output>
 --fetch --output <new external dir>
Only exact public Git blobs are fetched if missing from the local object store.
"""
import argparse,hashlib,html,json,re,subprocess,urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
R13="5c91e6b7eee91a432dc988f38f2e42bfbf6fa00a"
INVENTORY="cdeb4a954aa77751b6b776419b93f4f9432d70d28d6a66f86fd4d101e21ccc69"
MANIFEST="66c02d9bda23b0424330596b6e74a14576be0259d31f4e1b5a5f8ba07cb251d5"
ROOT="https://raw.githubusercontent.com/bitmaster162/ai-skill-lab/"
INPUTS={
"package.json":"a853089644c843c34f612a331ecff2b424841955",
"next.config.ts":"4a479ed4a4fa373095cd238fa67e40eb23d217c0",
"components/PhuketUniverse.tsx":"a478fe67234ef846fea295150740467500522d38",
"components/phuketUniverseMarkup.ts":"f89c6a18dae347c7246dd0ec7d2d1097a0c4e946",
"components/phuketUniverseAgencyTerms.ts":"605fd657d897205085f59a26dd9168f3d4928afb",
"components/phuketHousingCatalog.ts":"af607b52f03843c63bec94d9ef802514b6ae5bb0",
"components/phuketUniverseU3.ts":"d4a67f320304f80504f438334619026b124ae4ff",
"data/phuket_housing_r6_sections.json":"9569e4b268d1aa7c3c3dec57bc86f1e5807b8e0b",
"app/(ru)/phuket-universe/page.tsx":"3df664e8a59c841a53b3093a1f740af15ba71786",
"app/(en)/en/phuket-universe/page.tsx":"aade07d8626c862ff86cbb1cbf6c33dd378bc9ef"}
KINDS=("journey","budget-calculator","shortlist","move-in","move-out")
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def literal(value):return json.dumps(value,ensure_ascii=False).replace("\u2028","\\u2028").replace("\u2029","\\u2029")
def write(root,files):
 for name,b in files.items():
  p=root/name;p.parent.mkdir(parents=True,exist_ok=True)
  with p.open("xb") as f:f.write(b)
class Tags(HTMLParser):
 def __init__(self,s):super().__init__(convert_charrefs=True);self.tags=[];self.feed(s);self.close()
 def handle_starttag(self,t,a):self.tags.append((t,dict(a)))
 def handle_startendtag(self,t,a):self.handle_starttag(t,a)
def section(s):
 point=s.index('id="homes"');start=s.rfind("<section ",0,point);end=s.index("</section>",point)+len("</section>")
 need(start>=0 and s.count('id="homes"')==1,"homes boundary")
 return s[start:end]
def build(repo,r13,fetch):
 def git(*v,check=True):
  p=subprocess.run(["git","--no-optional-locks","-C",str(repo),*v],capture_output=True,timeout=20)
  if check:need(p.returncode==0,"git "+v[0])
  return p
 need(git("rev-parse",BASE+"^{commit}").stdout.decode().strip()==BASE,"Git baseline")
 tree={}
 for row in git("ls-tree","-r",BASE).stdout.decode().splitlines():
  meta,n=row.split("\t",1);mode,typ,oid=meta.split()
  if typ=="blob":tree[n]=oid
 def get(name,pin=None):
  expected=tree.get(name);need(expected and (pin is None or expected==pin),"exact Git tree "+name)
  q=git("show",BASE+":"+name,check=False)
  if q.returncode==0:b=q.stdout
  else:
   need(fetch,"missing local object; explicit --fetch required")
   req=urllib.request.Request(ROOT+BASE+"/"+quote(name,safe="/"),headers={"User-Agent":"Phuket-R14-Pinned-Review"})
   with urllib.request.urlopen(req,timeout=15) as f:b=f.read(200001)
  need(len(b)<=200000 and blob(b)==expected,"Git blob "+name)
  return b
 inputs={n:get(n,pin) for n,pin in INPUTS.items()}
 need(json.loads(inputs["package.json"])["dependencies"]["next"]=="16.3.6","Next version")
 parent=get("deploy/live/_release.json");need(sha(parent)==MANIFEST,"parent manifest")
 rows={x["path"]:x for x in json.loads(parent)["files"]}
 invraw=(r13/"DRAFT_INVENTORY.json").read_bytes();need(sha(invraw)==INVENTORY,"R13 report")
 inv=json.loads(invraw);need(inv["status"]=="DRAFT_ONLY_NOT_ADMITTED" and inv["base"]==BASE,"R13 scope")
 static={}
 for n,v in inv["overlay"].items():
  b=(r13/"overlay"/n).read_bytes();need(sha(b)==v["sha256"] and len(b)==v["bytes"],"R13 file "+n);static[n]=b
 need(len(static)==21,"overlay inventory")
 sections=json.loads(inputs["data/phuket_housing_r6_sections.json"])
 need(sections["listings_count"]==0,"empty reviewed catalogue")
 gateways={};tails={};expected_sections={}
 for l in ("ru","en"):
  n=("en/" if l=="en" else "")+"phuket-universe.html"
  s=section(static[n].decode())
  match=re.findall(r'<div[^>]*id="rental-journey-entry"[^>]*>.*?</div>',s,re.S)
  need(len(match)==1,"one exact static gateway")
  gateway=match[0];old=sections[l];tail=old[old.rfind('<p class="pu-s095">'):]
  need(tail.endswith("</p>\n</div>\n</section>") and old.count(tail)==1,"exact section tail")
  updated=old[:-len(tail)]+tail.replace("\n</div>\n</section>","\n"+gateway+"\n</div>\n</section>",1)
  need(updated==s,"static/Next section parity "+l)
  gateways[l]=gateway;tails[l]=tail;expected_sections[l]=s
 helper=("export type RentalJourneyLocale = \"ru\" | \"en\";\n"
 +"const gateways = "+literal(gateways)+" as const;\n"
 +"const tails = "+literal(tails)+" as const;\n"
 +"""export function withRentalJourney(markup: string, locale: RentalJourneyLocale): string {
  if (locale !== "ru" && locale !== "en") throw new Error("Unknown rental locale");
  const marker = 'id="homes"';
  if (markup.split(marker).length !== 2 || markup.includes('id="rental-journey-entry"')) throw new Error("Rental gateway boundary");
  const start = markup.indexOf(marker);
  const end = markup.indexOf("</section>", start) + "</section>".length;
  const tail = tails[locale];
  const i = markup.indexOf(tail, start);
  if (end < start || i < start || i + tail.length !== end || markup.split(tail).length !== 2) throw new Error("Rental section drift");
  const next = tail.replace("\\n</div>\\n</section>", "\\n" + gateways[locale] + "\\n</div>\\n</section>");
  if (next === tail) throw new Error("Rental insertion drift");
  return markup.slice(0, i) + next + markup.slice(i + tail.length);
}
""").encode()
 comp=inputs["components/PhuketUniverse.tsx"].decode()
 old="const markup = withUniverseU3(withHousingCatalog(withAgencyPilotTerms(phuketUniverseMarkup[locale], locale), locale), locale);"
 new="const markup = withRentalJourney(withUniverseU3(withHousingCatalog(withAgencyPilotTerms(phuketUniverseMarkup[locale], locale), locale), locale), locale);"
 need(comp.count(old)==1 and "withRentalJourney" not in comp,"component boundary")
 comp='import { withRentalJourney } from "@/components/phuketRentalJourney";\n'+comp.replace(old,new,1)
 out={"components/phuketRentalJourney.ts":helper,"components/PhuketUniverse.tsx":comp.encode()}
 route_rows=[]
 for l in ("ru","en"):
  prefix=("en/" if l=="en" else "")+"phuket-universe/"
  group="app/(en)/en/" if l=="en" else "app/(ru)/"
  for k in KINDS:
   static_path=prefix+"rental-"+k+".html";b=static[static_path];s=b.decode();tags=Tags(s).tags
   policies=[a["content"] for t,a in tags if t=="meta" and a.get("http-equiv","").lower()=="content-security-policy"]
   need(len(policies)==1,"page CSP")
   need(any(t=="meta" and a.get("name")=="robots" and a.get("content")=="noindex,nofollow" for t,a in tags),"noindex")
   headers={"Content-Type":"text/html; charset=utf-8","Content-Security-Policy":policies[0]+"; frame-ancestors 'none'; worker-src 'none'","X-Robots-Tag":"noindex, nofollow","Cache-Control":"no-store","X-Content-Type-Options":"nosniff","X-Frame-Options":"DENY","Referrer-Policy":"no-referrer","Permissions-Policy":"camera=(), microphone=(), geolocation=()"}
   name=group+prefix.removeprefix("en/")+"rental-"+k+"/route.ts"
   need(not any(x.startswith(name.rsplit("/",1)[0]+"/") for x in tree),"route directory collision")
   code="export const dynamic = \"force-static\";\nexport function GET(): Response {\n  return new Response("+literal(s)+", { status: 200, headers: "+literal(headers)+" });\n}\n"
   out[name]=code.encode();route_rows.append({"route":"/"+static_path[:-5],"handler":name,"static_path":static_path,"body_sha256":sha(b),"headers":headers})
 for n,b in static.items():
  if n.startswith("phuket-rental-assets/"):out["public/"+n]=b
 css=get("deploy/live/phuket-universe.css")
 need(sha(css)==rows["phuket-universe.css"]["sha256"],"guide CSS")
 out["public/phuket-universe.css"]=css
 for name in ("Unbounded-ru-en.woff2","Manrope-latin.woff2","Manrope-cyrillic.woff2"):
  path="fonts/"+name
  need(tree.get("public/"+path)==tree.get("deploy/live/"+path) and tree.get("public/"+path),"existing public font identity")
 need(len(out)==22 and set(out)&set(tree)=={"components/PhuketUniverse.tsx"},"exact additions/replacement")
 report={"scope":"NEXT_SOURCE_OVERLAY_DRAFT_ONLY","base":BASE,"r13":R13,"next_version":"16.3.6","input_blobs":{n:blob(b) for n,b in inputs.items()},"files":{n:{"sha256":sha(b),"bytes":len(b)} for n,b in out.items()},"routes":route_rows,"gateway":{l:{"fragment":gateways[l],"housing_sha256":sha(expected_sections[l].encode())} for l in gateways},"release_approval":False,"limitations":"Exact source overlay only. Node handler execution and pure renderer composition can be tested separately; actual Next build, route resolution, deployment, static release admission, full preflight and independent review remain open."}
 return out,inputs,report
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--repo",type=Path,required=True);p.add_argument("--r13",type=Path,required=True);p.add_argument("--fetch",action="store_true");p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 repo=a.repo.resolve();r13=a.r13.resolve();out=a.output.resolve()
 need(not out.exists() and all(out!=x and x not in out.parents for x in (repo,r13)),"new external output")
 files,inputs,report=build(repo,r13,a.fetch)
 out.mkdir(parents=True,exist_ok=False);write(out/"overlay",files);write(out/"inputs",inputs)
 write(out,{"NEXT_DRAFT.json":(json.dumps(report,indent=2,ensure_ascii=False)+"\n").encode()})
 print("NEXT_OVERLAY",len(files),"files",len(report["routes"]),"routes","report SHA256",sha((out/"NEXT_DRAFT.json").read_bytes()),flush=True)
if __name__=="__main__":main()
