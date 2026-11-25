"""R16 full static review package from the exact R15 handoff and Git baseline.
Build: python materialize_static.py --repo <pinned Git object store> --handoff <R15 candidate> --fetch --output <new dir>
Verify: python materialize_static.py --verify <R16 bundle>
No release manifest in the candidate root. No checkout, admission, or deployment.
"""
import argparse,hashlib,json,os,subprocess,urllib.request
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path,PurePosixPath
from urllib.parse import quote,urlsplit
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
R15="a02a1c3dfbba08feba9dc8de6e429938d2466020"
PARENT="66c02d9bda23b0424330596b6e74a14576be0259d31f4e1b5a5f8ba07cb251d5"
HANDOFF="7b392b647d4cf6c589f20fb8f793a3eb64f80a2a7b02c479f10732898733778c"
PARENT_PAYLOAD="f11a64758e9c5661eea55a24b9a98c6c078e17dcdfca8e335bd04c23776d99e5"
CANDIDATE_PAYLOAD="fdafd70fc29756d9ebc5c8d05bc9c3ca570189ce9d58b203d3e417f2c006176e"
ROOT="https://raw.githubusercontent.com/bitmaster162/ai-skill-lab/"
PREFIX="deploy/live/"
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def pathcheck(n):
 p=PurePosixPath(n)
 need(n and p.parts and n==p.as_posix() and not p.is_absolute() and ".." not in p.parts and "\\" not in n and ":" not in n,"unsafe path "+n)
def checked(raw,pin,msg):
 need(sha(raw)==pin,msg);return raw
def records(rows):
 out={}
 for r in rows:
  n=r["path"];pathcheck(n);need(n not in out and 0<=r["size"]<=200000,"invalid row "+n)
  out[n]={"path":n,"size":r["size"],"sha256":r["sha256"]}
 return out
def measure(files):
 return {"files":len(files),"payload_sha256":sha("".join(f"{n}\t{len(b)}\t{sha(b)}\n" for n,b in sorted(files.items())).encode()),"total_bytes":sum(map(len,files.values())),"nonfont_bytes":sum(len(b) for n,b in files.items() if not n.endswith(".woff2"))}
def verify_files(files,rows,payload):
 need(set(files)==set(rows),"file inventory mismatch")
 for n,b in files.items():
  r=rows[n];need(len(b)==r["size"] and sha(b)==r["sha256"],"file bytes "+n)
 m=measure(files);need(m["payload_sha256"]==payload,"payload digest");return m
def expected(parent_raw,handoff_raw):
 p=json.loads(checked(parent_raw,PARENT,"parent manifest pin"))
 h=json.loads(checked(handoff_raw,HANDOFF,"R15 handoff pin"))
 need(p["release_id"]=="AISL_RESTORED_GUIDES_R1_20261122" and p["payload_sha256"]==PARENT_PAYLOAD and p["file_count"]==116,"parent identity")
 need(h["base"]==BASE and h["scope"]=="R15_HANDOFF_DRAFT_ONLY" and not h["release_approval"],"handoff scope")
 rows=records(p["files"]);need(len(rows)==116 and "_release.json" not in rows,"parent inventory")
 target=dict(rows);changes={}
 for v in h["files"]:
  if not v["path"].startswith(PREFIX):continue
  n=v["path"][len(PREFIX):];pathcheck(n);need(n not in changes,"duplicate overlay")
  need(v["operation"]==("replace" if n in rows else "add"),"operation "+n)
  target[n]={"path":n,"size":v["bytes"],"sha256":v["sha256"]};changes[n]=v
 need(len(changes)==21 and set(rows)&set(changes)=={"phuket-universe.html","en/phuket-universe.html"},"21 file delta")
 need(len(target)==135 and h["static_payload_projection"]["sha256"]==CANDIDATE_PAYLOAD,"135 file projection")
 return rows,target,changes
def read_dir(root):
 need(root.is_dir() and not root.is_symlink(),"regular directory")
 result={}
 for f in root.rglob("*"):
  need(not f.is_symlink(),"symlink "+str(f))
  if f.is_dir():continue
  need(f.is_file(),"regular file "+str(f))
  n=f.relative_to(root).as_posix();pathcheck(n);need(f.stat().st_size<=200000,"file bound "+n)
  result[n]=f.read_bytes()
 return result
def write(root,files):
 for n,b in files.items():
  pathcheck(n);p=root/n;p.parent.mkdir(parents=True,exist_ok=True)
  with p.open("xb") as f:f.write(b)
def verify_bundle(folder):
 pr=(folder/"provenance"/"parent_manifest.json").read_bytes()
 hr=(folder/"provenance"/"handoff.json").read_bytes()
 rows,target,changes=expected(pr,hr)
 before=read_dir(folder/"parent");after=read_dir(folder/"static")
 a=verify_files(before,rows,PARENT_PAYLOAD);b=verify_files(after,target,CANDIDATE_PAYLOAD)
 actual={n for n,v in after.items() if n not in before or before[n]!=v}
 need(actual==set(changes),"exact delta")
 need(a["total_bytes"]==1516366 and a["nonfont_bytes"]==1394978,"parent measured size")
 need(b["nonfont_bytes"]==1491332 and b["nonfont_bytes"]-a["nonfont_bytes"]==96354,"candidate measured size")
 return {"parent":a,"candidate":b,"verified_parent_files":116,"verified_candidate_files":135,"unchanged_parent_files":114,"changed_or_added":21}
def build(repo,handoff,folder,fetch):
 env={**os.environ,"GIT_NO_LAZY_FETCH":"1","GIT_ALLOW_PROTOCOL":"","GIT_TERMINAL_PROMPT":"0","GIT_CONFIG_NOSYSTEM":"1","GIT_CONFIG_GLOBAL":os.devnull}
 def git(*a,input=None):
  return subprocess.check_output(["git","--no-optional-locks","-C",str(repo),*a],input=input,env=env,timeout=20)
 need(git("rev-parse",BASE+"^{commit}").decode().strip()==BASE,"Git baseline")
 parent_raw=git("show",BASE+":"+PREFIX+"_release.json")
 handoff_raw=(handoff/"HANDOFF.json").read_bytes()
 rows,target,changes=expected(parent_raw,handoff_raw)
 tree={}
 for line in git("ls-tree","-r",BASE,"deploy/live").decode().splitlines():
  meta,n=line.split("\t",1);mode,typ,oid=meta.split()
  need(mode=="100644" and typ=="blob" and n.startswith(PREFIX),"regular Git blob")
  tree[n[len(PREFIX):]]=oid
 need(set(tree)==set(rows)|{"_release.json"},"parent tree inventory")
 need(blob(parent_raw)==tree["_release.json"],"manifest Git blob")
 oids=sorted(set(tree[n] for n in rows))
 lines=git("cat-file","--batch-check",input=("\n".join(oids)+"\n").encode()).decode().splitlines()
 need(len(lines)==len(oids),"object availability result")
 present={line.split()[0] for line in lines if len(line.split())==3 and line.split()[1]=="blob"}
 def get(n):
  oid=tree[n];r=rows[n]
  if oid in present:
   b=git("cat-file","blob",oid);source="local_git"
  else:
   need(fetch,"missing Git object "+n+"; explicit --fetch required")
   url=ROOT+BASE+"/"+quote(PREFIX+n,safe="/")
   req=urllib.request.Request(url,headers={"User-Agent":"Phuket-R16-Pinned-Static-Review"})
   with urllib.request.urlopen(req,timeout=15) as f:
    need(urlsplit(f.geturl()).hostname=="raw.githubusercontent.com","unexpected source host")
    b=f.read(r["size"]+1)
   source="immutable_raw_github"
  need(len(b)==r["size"] and sha(b)==r["sha256"] and blob(b)==oid,"parent byte identity "+n)
  return n,b,source
 parent={};sources={}
 with ThreadPoolExecutor(max_workers=6) as ex:
  pending=[ex.submit(get,n) for n in sorted(rows)]
  for job in as_completed(pending):
   n,b,source=job.result();parent[n]=b;sources[n]={"source":source,"git_blob":tree[n],"sha256":sha(b)}
   if len(parent)%16==0 or len(parent)==116:print("PARENT_VERIFIED",len(parent),"/116",flush=True)
 a=verify_files(parent,rows,PARENT_PAYLOAD)
 candidate=dict(parent)
 for n,v in changes.items():
  f=handoff/"overlay"/v["path"];need(f.is_file() and not f.is_symlink(),"regular overlay "+n)
  raw=f.read_bytes();need(len(raw)==v["bytes"] and sha(raw)==v["sha256"],"overlay pin "+n);candidate[n]=raw
 b=verify_files(candidate,target,CANDIDATE_PAYLOAD)
 need(b["nonfont_bytes"]==1491332 and b["nonfont_bytes"]-a["nonfont_bytes"]==96354,"measured nonfont")
 def rejected(fn):
  try:fn()
  except ValueError:return True
  return False
 key="phuket-universe/rental-journey.html"
 checks={
  "parent_tamper_rejected":rejected(lambda:verify_files({**parent,"phuket-universe.html":parent["phuket-universe.html"]+b" "},rows,PARENT_PAYLOAD)),
  "candidate_tamper_rejected":rejected(lambda:verify_files({**candidate,key:candidate[key]+b" "},target,CANDIDATE_PAYLOAD)),
  "missing_file_rejected":rejected(lambda:verify_files({n:v for n,v in candidate.items() if n!=key},target,CANDIDATE_PAYLOAD)),
  "extra_file_rejected":rejected(lambda:verify_files({**candidate,"unexpected.html":b"noindex"},target,CANDIDATE_PAYLOAD)),
  "manifest_tamper_rejected":rejected(lambda:expected(parent_raw+b" ",handoff_raw)),
  "handoff_tamper_rejected":rejected(lambda:expected(parent_raw,handoff_raw+b" "))}
 need(all(checks.values()),"negative checks")
 folder.mkdir(exist_ok=False,parents=True)
 write(folder/"provenance",{"parent_manifest.json":parent_raw,"handoff.json":handoff_raw})
 write(folder/"parent",parent);write(folder/"static",candidate)
 observed=verify_bundle(folder);need(observed["parent"]==a and observed["candidate"]==b,"disk readback")
 report={"scope":"R16_FULL_STATIC_REVIEW_ONLY","base":BASE,"r15":R15,"parent_manifest_sha256":PARENT,"handoff_sha256":HANDOFF,"observed":observed,"parent_sources":sources,"negative_checks":checks,"release_approval":False,"limitations":"All static payload bytes materialized and verified. No candidate _release.json, no full preflight, Next build, successor admission, independent review or production deployment. Parent manifest and R15 handoff saved only as provenance."}
 raw=(json.dumps(report,indent=2,sort_keys=True)+"\n").encode()
 write(folder,{"MATERIALIZED.json":raw})
 print("MATERIALIZED",a["files"],b["files"],"unchanged",observed["unchanged_parent_files"],"negative",sum(checks.values()),"/",len(checks),"nonfont",b["nonfont_bytes"],"payload",b["payload_sha256"],"report SHA256",sha(raw),flush=True)
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--repo",type=Path);p.add_argument("--handoff",type=Path);p.add_argument("--fetch",action="store_true");p.add_argument("--output",type=Path);p.add_argument("--verify",type=Path);a=p.parse_args()
 if a.verify:
  need(not(a.repo or a.handoff or a.fetch or a.output),"verify mode only")
  print(json.dumps(verify_bundle(a.verify.resolve()),indent=2));return
 need(a.repo and a.handoff and a.output,"build parameters required")
 repo=a.repo.resolve();handoff=a.handoff.resolve();folder=a.output.resolve()
 need(not folder.exists() and all(folder!=x and x not in folder.parents for x in (repo,handoff)),"new external output")
 build(repo,handoff,folder,a.fetch)
if __name__=="__main__":main()
