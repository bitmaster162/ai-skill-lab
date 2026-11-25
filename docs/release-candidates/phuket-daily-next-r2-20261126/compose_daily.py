"""Daily essentials R2: compose exact R20 rental and Daily R1, add Next parity.
Review only. Run: python compose_daily.py --evidence-root <Phuket evidence>
 --repo <pinned Git object store> --output <new directory>
No active checkout, release manifest, historical policy or deployment writes.
"""
import argparse,hashlib,json,os,re,subprocess,base64
from pathlib import Path
from html.parser import HTMLParser
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
R20="7f51fe030fa0e0dc5258c646e705d6f92ac8bd8341ca0bff2f76b3ca76ed6f53"
PROFILE="5c91d5044cec3737d64289e49daad86d2ed786581d7d3af1dbe7bf0491f280a0"
DAILY="c13717ecafb21cb37ce53e282383c67c2df0b27a24617182d92057364781a36a"
DAILY_QA="8b50bd548cbbdecf69193dda8490b252c9663566a84b1bf1909aebb264baa7d5"
PATCHER="6e5a6e24f63bf5ae9012725254ea10ea5c1a177b9584891cd2708122e7a5902b"
R14="b0922405e3741470b449e90e5e0e85681170ce6c7e1f4989161d41fe2d029e8e"
PARENT="f11a64758e9c5661eea55a24b9a98c6c078e17dcdfca8e335bd04c23776d99e5"
RENTAL="fca36841bb4a352296c46191f994d050cecb74017e3e74c18349f55ce4d132ed"
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def checked(p,pin):
 b=p.read_bytes();need(sha(b)==pin,"pin "+str(p));return b
def read(p):
 out={}
 for f in sorted(p.rglob("*")):
  need(not f.is_symlink(),"symlink")
  if f.is_file():out[f.relative_to(p).as_posix()]=f.read_bytes()
 return out
def digest(files):return sha("".join(f"{n}\t{len(b)}\t{sha(b)}\n" for n,b in sorted(files.items())).encode())
def encode(o):return (json.dumps(o,indent=2,ensure_ascii=False,sort_keys=True)+"\n").encode()
def literal(s):return json.dumps(s,ensure_ascii=False).replace("\u2028","\\u2028").replace("\u2029","\\u2029")
def once(s,a,b):
 need(s.count(a)==1,"unique boundary "+a[:80]);return s.replace(a,b,1)
class Tags(HTMLParser):
 def __init__(self,s):super().__init__(convert_charrefs=True);self.tags=[];self.feed(s);self.close()
 def handle_starttag(self,t,a):self.tags.append((t,dict(a)))
 def handle_startendtag(self,t,a):self.handle_starttag(t,a)
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ("evidence-root","repo","output"):p.add_argument("--"+n,type=Path,required=True)
 a=p.parse_args();root=a.evidence_root.resolve();repo=a.repo.resolve();out=a.output.resolve()
 need(not out.exists() and out!=root and out!=repo and repo not in out.parents,"new external output")
 env={**os.environ,"GIT_NO_LAZY_FETCH":"1","GIT_ALLOW_PROTOCOL":"","GIT_TERMINAL_PROMPT":"0","GIT_CONFIG_NOSYSTEM":"1","GIT_CONFIG_GLOBAL":os.devnull}
 def git(*v,cwd=None):return subprocess.check_output(["git","--no-optional-locks",*v],env=env,cwd=cwd,timeout=25,stderr=subprocess.STDOUT)
 need(git("-C",str(repo),"rev-parse",BASE+"^{commit}").decode().strip()==BASE,"Git baseline")
 def d(name):return root/("L12_"+name+"_20261126")
 p20=d("FONT_PROFILE_R20")/"candidate";pd=d("DAILY_ESSENTIALS_R1");p14=d("NEXT_PARITY_R14")/"candidate"
 m=json.loads(checked(p20/"R20.json",R20))
 prof=json.loads(checked(d("SUCCESSOR_PROFILE_R21")/"candidate"/"PROFILE_DRAFT.json",PROFILE))
 daily=json.loads(checked(pd/"candidate"/"DAILY_DRAFT.json",DAILY));qa=json.loads(checked(pd/"qa"/"QA.json",DAILY_QA))
 need(all(x["base"]==BASE and not x["release_approval"] for x in (m,prof,daily)) and qa["all_pass"] and qa["passed"]==qa["total"]==110,"draft scope")
 static=read(p20/"static");nxt=read(p20/"next");parent=read(d("STATIC_CANDIDATE_R16")/"bundle"/"parent")
 need(len(parent)==116 and digest(parent)==PARENT and len(static)==136 and digest(static)==RENTAL,"exact payloads")
 for files,key in ((static,"static_files"),(nxt,"next_files")):
  need(set(files)==set(prof[key]),"inventory")
  for n,b in files.items():need(sha(b)==prof[key][n]["sha256"] and len(b)==prof[key][n]["bytes"],"profile "+n)
 ds=read(pd/"candidate"/"overlay");need(set(ds)==set(daily["delta"]) and len(ds)==6,"Daily delta")
 for n,b in ds.items():need(sha(b)==daily["delta"][n]["sha256"] and len(b)==daily["delta"][n]["bytes"],"Daily pin")
 marker='<section class="pu-s039" id="agencies">'
 sections={};combined=dict(static);next_combined=dict(nxt);route_rows=[]
 for l in ("ru","en"):
  n=("en/" if l=="en" else "")+"phuket-universe.html"
  s=ds[n].decode()
  part=re.findall(r'<section class="pu-s039" id="daily-essentials"[^>]*>.*?</section>\n\n',s,re.S)
  need(len(part)==1 and once(s,part[0],"").encode()==parent[n],"Daily insertion only")
  sections[l]=part[0]
  combined[n]=once(static[n].decode(),marker,part[0]+marker).encode()
  need(once(combined[n].decode(),part[0],"").encode()==static[n],"rental gateway preserved")
  path=n[:-5]+"/daily-essentials.html";need(path not in combined,"new route")
  raw=ds[path];combined[path]=raw
  tags=Tags(raw.decode()).tags
  csp=[x["content"] for t,x in tags if t=="meta" and x.get("http-equiv","").lower()=="content-security-policy"]
  need(len(csp)==1 and any(t=="meta" and x.get("name")=="robots" and x.get("content")=="noindex,nofollow" for t,x in tags),"restrictive metadata")
  headers={"Content-Type":"text/html; charset=utf-8","Content-Security-Policy":csp[0]+"; frame-ancestors 'none'; worker-src 'none'","X-Robots-Tag":"noindex, nofollow","Cache-Control":"no-store","X-Content-Type-Options":"nosniff","X-Frame-Options":"DENY","Referrer-Policy":"no-referrer","Permissions-Policy":"camera=(), microphone=(), geolocation=()"}
  handler=("app/(en)/en/" if l=="en" else "app/(ru)/")+"phuket-universe/daily-essentials/route.ts"
  next_combined[handler]=("export const dynamic = \"force-static\";\nexport function GET(): Response {\n  return new Response("+literal(raw.decode())+", { status: 200, headers: "+literal(headers)+" });\n}\n").encode()
  route_rows.append({"route":"/"+path[:-5],"html_path":path,"handler":handler,"body_sha256":sha(raw),"headers":headers})
 for n,b in ds.items():
  if n.startswith("phuket-daily-assets/"):
   need(n not in combined and "public/"+n not in next_combined,"new asset")
   combined[n]=b;next_combined["public/"+n]=b
 helper=("export type DailyLocale = \"ru\" | \"en\";\nconst sections = "+literal(sections)+" as const;\n"
 +"""export function withDailyEssentials(markup: string, locale: DailyLocale): string {
  if (locale !== "ru" && locale !== "en") throw new Error("Unknown daily locale");
  const marker = '<section class="pu-s039" id="agencies">';
  if (markup.split(marker).length !== 2 || markup.includes('id="daily-essentials"')) throw new Error("Daily gateway boundary");
  return markup.replace(marker, sections[locale] + marker);
}
""").encode()
 next_combined["components/phuketDailyEssentials.ts"]=helper
 n="components/PhuketUniverse.tsx";old_comp=nxt[n].decode()
 old_line="const markup = withRentalJourney(withUniverseU3(withHousingCatalog(withAgencyPilotTerms(phuketUniverseMarkup[locale], locale), locale), locale), locale);"
 new_line="const markup = withDailyEssentials(withRentalJourney(withUniverseU3(withHousingCatalog(withAgencyPilotTerms(phuketUniverseMarkup[locale], locale), locale), locale), locale), locale);"
 next_combined[n]=('import { withDailyEssentials } from "@/components/phuketDailyEssentials";\n'+once(old_comp,old_line,new_line)).encode()
 sd={n for n,b in combined.items() if static.get(n)!=b};nd={n for n,b in next_combined.items() if nxt.get(n)!=b}
 need(sd==set(ds) and len(nd)==6 and len(combined)==140 and len(next_combined)==28,"exact incremental delta")
 for n in static:
  if n not in sd:need(combined[n]==static[n],"rental bytes preserved")
 need(all(next_combined[n]==nxt[n] for n in nxt if n!="components/PhuketUniverse.tsx"),"rental Next preserved")
 # Construct the complete review patch against original main, not a patch
 # requiring the earlier draft to have been merged.
 tree={}
 for line in git("-C",str(repo),"ls-tree","-r",BASE).decode().splitlines():
  meta,n=line.split("\t",1);mode,typ,oid=meta.split()
  if typ=="blob":tree[n]=(mode,oid)
 changed={n for n,b in combined.items() if parent.get(n)!=b}
 files={**{"deploy/live/"+n:combined[n] for n in changed},**next_combined}
 old={"deploy/live/"+n:parent[n] for n in changed if n in parent}
 rp=json.loads(checked(p14/"NEXT_DRAFT.json",R14));old["components/PhuketUniverse.tsx"]=(p14/"inputs/components/PhuketUniverse.tsx").read_bytes()
 need(len(files)==54 and len(old)==3 and set(files)&set(tree)==set(old) and all(tree[n]==("100644",blob(b)) for n,b in old.items()),"exact 54 file baseline scope")
 need(rp["input_blobs"]["components/PhuketUniverse.tsx"]==blob(old["components/PhuketUniverse.tsx"]),"component pin")
 source=checked(d("TOOLKIT_REVIEW_R22")/"build_review_patch.py",PATCHER);ns={"__name__":"pinned_patch"};exec(compile(source,"pinned_patch.py","exec"),ns)
 patch=b"".join(ns["patch_for"](n,old.get(n),b) for n,b in sorted(files.items()))
 need(len(patch)<600000,"small patch")
 out.mkdir(parents=True,exist_ok=False)
 ns["write"](out/"static",combined);ns["write"](out/"next",next_combined)
 ns["write"](out,{"combined.patch":patch,"patch.b64":base64.encodebytes(patch)})
 work=out/"apply_check";work.mkdir();ns["write"](work,old)
 args=("apply","--whitespace=nowarn")
 git(*args,"--check",str(out/"combined.patch"),cwd=work);git(*args,str(out/"combined.patch"),cwd=work)
 need(read(work)==files,"54 exact postimages");git(*args,"--reverse","--check",str(out/"combined.patch"),cwd=work)
 report={"scope":"DAILY_R2_COMBINED_REVIEW_ONLY","base":BASE,"r20_payload":RENTAL,"static_payload":digest(combined),"static_files":len(combined),"next_files":len(next_combined),"incremental_static":sorted(sd),"incremental_next":sorted(nd),"daily_routes":route_rows,"gateways":sections,"patch_sha256":sha(patch),"patch_git_blob":blob(patch),"patch_bytes":len(patch),"patch_files":{n:{"sha256":sha(b),"bytes":len(b),"git_blob":blob(b)} for n,b in sorted(files.items())},"all_54_postimages_exact":True,"release_approval":False,"limitations":"Combined rental and daily candidate, not applied to checkout. Two additional noindex tool routes require successor policy review. Actual Next build/router, full preflight, independent review, visual acceptance and release admission open."}
 raw=encode(report);ns["write"](out,{"COMBINED_DRAFT.json":raw})
 print("COMBINED",len(combined),"static",len(next_combined),"Next",len(files),"patch files",len(patch),"bytes","payload",report["static_payload"],"report",sha(raw),"patch",sha(patch),"blob",blob(patch),"base64 lines",len(base64.encodebytes(patch).splitlines()),flush=True)
if __name__=="__main__":main()
