"""R21 exact proposed successor profile and scoped review checks.
Run: python review_successor.py --evidence-root <Phuket Universe evidence folder> --repo <pinned Git store> --output <new directory>
All inputs are existing pinned artifacts. No network, checkout writes, active
policy edits, approval, manifest issuance, build, or deployment.
"""
import argparse,hashlib,json,os,subprocess
from pathlib import Path
from html.parser import HTMLParser
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
R20_COMMIT="b77cd16f44a6ba31ad39117273b3cf91f20f9258"
PAYLOAD="fca36841bb4a352296c46191f994d050cecb74017e3e74c18349f55ce4d132ed"
PARENT_PAYLOAD="f11a64758e9c5661eea55a24b9a98c6c078e17dcdfca8e335bd04c23776d99e5"
DIRS={n:("L12_"+s+"_20261126") for n,s in [
 (14,"NEXT_PARITY_R14"),(15,"TOOLKIT_HANDOFF_R15"),(16,"STATIC_CANDIDATE_R16"),(17,"STATIC_AUDIT_R17"),(18,"SKIP_NAVIGATION_R18"),(19,"GUIDE_COMPACT_R19"),(20,"FONT_PROFILE_R20")]}
PINS={
 (14,"candidate/NEXT_DRAFT.json"):"b0922405e3741470b449e90e5e0e85681170ce6c7e1f4989161d41fe2d029e8e",
 (15,"assemble_handoff.py"):"a4b7d128f896c9d4ca7e8efec35e8733167bff94c2712f91f1571555606feaa1",
 (16,"bundle/MATERIALIZED.json"):"12dd8ea46e38216d2c8973fee476e768b3db66893a5d4766aefd70e64758c033",
 (17,"audit_static_revised.py"):"087ac2bb2f1db9b1ac4207744435fcc75935b2513e2b06aa77ed837154d3f60d",
 (17,"audit_revised/AUDIT.json"):"044f0428c6e3cd04a5fdc8188322e2bee77c58689e8ae4ce219d8d2a9931e9d5",
 (17,"audit_revised/measure_pinned.mjs"):"16520f212967e1aece6646be4f4aa4ad4b60a17d0012254b0c1505e653acdd82",
 (18,"candidate/R18.json"):"2c9641546e4d800cb1f024064e41c1480a0ebc62e328ead60c5ceecb0defece2",
 (19,"candidate/R19.json"):"57bb2559e5f7128f99ab30ae42a194bcec6d9a3e1b94d2cf1c4cbcfbe54c718c",
 (20,"system_fonts.py"):"178c64bff114250e52fe09854417e7eec3f31304a63a499f36814175256e7454",
 (20,"candidate/R20.json"):"7f51fe030fa0e0dc5258c646e705d6f92ac8bd8341ca0bff2f76b3ca76ed6f53",
 (20,"qa/QA.json"):"da46cf55f2e967b090d8a2cf98ae8b6996868282fc1a51f2a0cf320723fd5aab"}
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def checked(p,pin):
 b=p.read_bytes();need(sha(b)==pin,"pin "+str(p));return b
def load(b,name):
 d={"__name__":name};exec(compile(b,name+".py","exec"),d);return d
def read(p):
 out={}
 for f in sorted(p.rglob("*")):
  need(not f.is_symlink(),"symlink")
  if f.is_file():out[f.relative_to(p).as_posix()]=f.read_bytes()
 return out
def encode(o):return (json.dumps(o,ensure_ascii=False,indent=2,sort_keys=True)+"\n").encode()
def records(files):return {n:{"sha256":sha(b),"bytes":len(b)} for n,b in sorted(files.items())}
def payload(files):return sha("".join(f"{n}\t{len(b)}\t{sha(b)}\n" for n,b in sorted(files.items())).encode())
def reject(fn):
 try:fn()
 except (ValueError,KeyError):return True
 return False
def build(root,repo):
 env={**os.environ,"GIT_NO_LAZY_FETCH":"1","GIT_ALLOW_PROTOCOL":"","GIT_TERMINAL_PROMPT":"0","GIT_CONFIG_NOSYSTEM":"1","GIT_CONFIG_GLOBAL":os.devnull}
 def git(*a):return subprocess.check_output(["git","--no-optional-locks","-C",str(repo),*a],env=env,timeout=25)
 need(git("rev-parse",BASE+"^{commit}").decode().strip()==BASE,"exact Git baseline")
 def at(n,p):return root/DIRS[n]/p
 src={k:checked(at(*k),v) for k,v in PINS.items()}
 def doc(n,p):return json.loads(src[n,p])
 r14=doc(14,"candidate/NEXT_DRAFT.json");r18=doc(18,"candidate/R18.json");r19=doc(19,"candidate/R19.json");r20=doc(20,"candidate/R20.json")
 qa=doc(20,"qa/QA.json");old_audit=doc(17,"audit_revised/AUDIT.json")
 need(all(x["base"]==BASE and not x["release_approval"] for x in (r14,r18,r19,r20)),"candidate scope")
 need(qa["all_pass"] and qa["passed"]==qa["total"]==255,"previous QA")
 route=load(src[15,"assemble_handoff.py"],"pinned_route")
 audit=load(src[17,"audit_static_revised.py"],"pinned_audit")
 fonts=load(src[20,"system_fonts.py"],"pinned_fonts")
 parent=read(at(16,"bundle/parent"));static=read(at(20,"candidate/static"));nxt=read(at(20,"candidate/next"))
 need(len(parent)==116 and payload(parent)==PARENT_PAYLOAD,"parent payload")
 need(len(static)==136 and payload(static)==PAYLOAD,"candidate payload")
 need(fonts["measure"](static)==r20["candidate_payload"],"actual candidate size")
 need(set(parent)<=set(static),"no parent removals")
 replaced=sorted(n for n in parent if parent[n]!=static[n]);added=sorted(set(static)-set(parent))
 need(replaced==["en/phuket-universe.html","phuket-universe.html"] and len(added)==20,"exact static delta")
 next_pins={**r14["files"],**r18["next_delta"],**r19["next_delta"],**r20["next_delta"]}
 need(len(nxt)==23 and set(nxt)==set(next_pins),"exact Next inventory")
 for n,v in nxt.items():need(len(v)==next_pins[n]["bytes"] and sha(v)==next_pins[n]["sha256"],"Next pin "+n)
 existing=set(git("ls-tree","-r","--name-only",BASE).decode().splitlines())
 need(set(nxt)&existing=={"components/PhuketUniverse.tsx"},"Next replacement scope")
 need(all(static[n[len("public/"):]]==v for n,v in nxt.items() if n.startswith("public/")),"public asset parity")
 tools=r20["font_policy_proposal"]
 pages={"/"+n[:-5]:static[n] for n in tools}
 admitted={r:sha(b) for r,b in pages.items()}
 partition=route["route_policy"](parent,static,pages,static["sitemap.xml"],admitted)
 need(fonts["font_policy"](static,tools),"exact font proposal")
 # Compare metadata for all 60 existing public documents, including the two
 # aggregator pages whose body changed. Do not exempt them from old rules.
 pins=audit["PINS"];gate={n:checked(at(17,"inputs/"+n),v) for n,v in pins.items()}
 parser=audit["source_class"](gate["scripts/check_static_release.py"],"PageParser")
 for n in parent:
  if n.endswith(".html"):
   def metadata(b):
    p=parser();p.feed(b.decode());p.close()
    return p.canonical,p.alternates,p.jsonld,p.forms
   need(metadata(parent[n])==metadata(static[n]),"parent metadata "+n)
 # New pages must match exact Next handler response bodies and header literals.
 rows={r["route"]:r for r in r18["routes"]}
 for r in r19["routes"]+r20["routes"]:rows[r["route"]]=r
 need(set(rows)==set(pages),"handler route set")
 for key,r in rows.items():
  s=nxt[r["handler"]].decode()
  marker="return new Response(";i=s.index(marker)+len(marker)
  body,end=json.JSONDecoder().raw_decode(s[i:])
  need(body.encode()==pages[key] and sha(body.encode())==r["body_sha256"],"handler body "+key)
  tail=s[i+end:];marker="headers: ";j=tail.index(marker)+len(marker)
  h,_=json.JSONDecoder().raw_decode(tail[j:])
  need(h==r["headers"] and h["X-Robots-Tag"]=="noindex, nofollow" and h["Cache-Control"]=="no-store","handler headers "+key)
 ac=audit["source_class"](gate["scripts/check_static_accessibility.py"],"Audit")
 sc=audit["source_class"](gate["scripts/check_security_headers.py"],"P")
 structural=audit["audit"](static,ac,parser,sc)
 prior=old_audit["results"]["parent"]["structural"]
 need(structural["issues"]==prior["issues"],"new structural issue "+str(structural["issues"]))
 # The four common _release.json links reflect the deliberately absent
 # review-only manifest. They are not silently removed from this report.
 need(len(prior["issues"])==4 and all(x["kind"]=="link" and x["detail"]=="/_release.json" for x in prior["issues"]),"known review-only findings")
 measure=at(17,"audit_revised/measure_pinned.mjs")
 z=subprocess.run(["node",str(measure),str(at(20,"candidate/static"))],capture_output=True,check=True,timeout=150)
 transfer=json.loads(z.stdout)
 need(len(transfer["rows"])==71 and not transfer["failures"],"full measurement")
 profile=json.loads(gate["data/phuket_universe_u3_e38_r7b_profile.json"])
 comparisons=audit["compare_metrics"](transfer,profile)
 expected={("historical_font_rule",n,"font preload count",0,2) for n in tools}
 observed={(x["kind"],x["file"],x["detail"],x.get("observed"),x.get("limit")) for x in comparisons}
 need(observed==expected and len(comparisons)==10,"unapproved comparison "+str(comparisons))
 need(transfer["sharedLabBr"]<=1344,"shared lab budget")
 prior_transfer=old_audit["results"]["parent"]["transfer"]["rows"]
 for n in prior_transfer:
  if n not in replaced:need(transfer["rows"][n]==prior_transfer[n],"existing transfer drift "+n)
 for n in tools:
  v=transfer["rows"][n];need(v["fontCount"]==v["fontBytes"]==0 and v["fonts"]==[],"font measurement "+n)
 need(all(v["font_requests"]==[] and v["pass"] for v in qa["cases"]),"pinned browser evidence")
 tests={}
 tests["modified_candidate_rejected"]=reject(lambda:need(payload({**static,"phuket-universe.html":static["phuket-universe.html"]+b" "})==PAYLOAD,"candidate digest"))
 tests["unknown_noindex_route_rejected"]=reject(lambda:route["route_policy"](parent,{**static,"phuket-universe/rental-extra.html":b"noindex"},pages,static["sitemap.xml"],admitted))
 tests["sitemap_missing_route_rejected"]=reject(lambda:route["route_policy"](parent,static,pages,static["sitemap.xml"].replace(b"<loc>https://aiskillab.work/</loc>",b"<loc>https://aiskillab.work/unknown</loc>",1),admitted))
 tests["unapproved_font_route_rejected"]=reject(lambda:fonts["font_policy"](static,{**tools,"index.html":tools[next(iter(tools))]}))
 tests["changed_css_rejected"]=reject(lambda:fonts["font_policy"]({**static,tools[next(iter(tools))]["css_path"]:b"@font-face{}"},tools))
 tests["changed_font_count_rejected"]=reject(lambda:fonts["font_policy"](static,{**tools,next(iter(tools)):{**tools[next(iter(tools))],"font_count":1}}))
 need(all(tests.values()),"negative checks "+str(tests))
 proposal={"schema":"phuket-rental-successor-profile.draft.v1","status":"PROPOSED_NOT_ADMITTED","base":BASE,"r20_commit":R20_COMMIT,"candidate_payload":r20["candidate_payload"],"parent_payload_sha256":PARENT_PAYLOAD,"static_replacements":replaced,"static_additions":added,"static_files":records(static),"next_files":records(nxt),"route_partition":partition,"font_policy_proposal":tools,"tool_byte_caps":{"htmlBr":10240,"cssBr":8192,"firstBr":19456,"firstGz":23040,"firstWithFonts":102400},"tool_observed_transfer":{n:transfer["rows"][n] for n in sorted(tools)},"historical_source_sha256":pins,"historical_rule_disposition":"Keep existing checks for all existing pages. Proposed exact ten-tool nonindex and zero-font rules only. Not installed or approved.","authority":{"merge":False,"deploy":False,"production":False},"open_gates":["Independent approval of exact successor profile and changed guide typography.","Implement separately versioned lineage/route/font checks without modifying historical seals.","Actual Next build/router, full preflight, accessibility/visual review and owner merge."],"release_approval":False}
 result={"scope":"R21_OWNER_PROPOSAL_CHECKS","status":"SCOPED_CHECKS_PASS_NOT_RELEASE_APPROVAL","structural_checks":structural["checks"],"structural_findings":structural["issues"],"historical_comparisons":comparisons,"negative_checks":tests,"prior_browser_and_node_qa":255,"transfer_pages":len(transfer["rows"]),"static_verified":len(static),"next_verified":len(nxt),"limitations":"Existing pinned parser and compression measurements, direct source body/header checks. Historical font count conflicts are retained, not passed. No actual Next build/router, independent acceptance, full preflight, approval or deployment.","release_approval":False}
 return proposal,result
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ("evidence-root","repo","output"):p.add_argument("--"+n,type=Path,required=True)
 a=p.parse_args();root=a.evidence_root.resolve();repo=a.repo.resolve();out=a.output.resolve()
 need(not out.exists() and out!=root and out!=repo and repo not in out.parents,"new external directory")
 proposal,result=build(root,repo);raw=encode(proposal);result["profile_sha256"]=sha(raw)
 out.mkdir(parents=True,exist_ok=False)
 for n,b in (("PROFILE_DRAFT.json",raw),("QA.json",encode(result))):
  with (out/n).open("xb") as f:f.write(b)
 print("PROPOSAL",len(proposal["static_files"]),"static",len(proposal["next_files"]),"Next",sum(result["structural_checks"].values()),"structural checks",len(result["historical_comparisons"]),"historical font conflicts",sum(result["negative_checks"].values()),"/",len(result["negative_checks"]),"negative",flush=True)
 print("PROFILE_SHA256",sha(raw),"QA_SHA256",sha((out/"QA.json").read_bytes()),flush=True)
if __name__=="__main__":main()
