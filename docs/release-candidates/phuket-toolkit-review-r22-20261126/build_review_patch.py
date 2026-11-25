"""R22 consolidated exact-source patch for review, NOT release admission.
Builds and verifies a unified patch in an isolated directory.
Run: python build_review_patch.py --evidence-root <Phuket Universe> --repo <pinned Git object store> --output <new external directory>
No tracked checkout changes or network.
"""
import argparse,difflib,hashlib,json,os,subprocess
from pathlib import Path,PurePosixPath
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
PROFILE="5c91d5044cec3737d64289e49daad86d2ed786581d7d3af1dbe7bf0491f280a0"
PAYLOAD="fca36841bb4a352296c46191f994d050cecb74017e3e74c18349f55ce4d132ed"
PARENT="f11a64758e9c5661eea55a24b9a98c6c078e17dcdfca8e335bd04c23776d99e5"
R14="b0922405e3741470b449e90e5e0e85681170ce6c7e1f4989161d41fe2d029e8e"
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def checked(p,pin):
 b=p.read_bytes();need(sha(b)==pin,"pin "+str(p));return b
def read(root):
 out={}
 for f in sorted(root.rglob("*")):
  need(not f.is_symlink(),"symlink")
  if f.is_file():out[f.relative_to(root).as_posix()]=f.read_bytes()
 return out
def digest(files):
 return sha("".join(f"{n}\t{len(b)}\t{sha(b)}\n" for n,b in sorted(files.items())).encode())
def write(root,files):
 for n,b in files.items():
  p=PurePosixPath(n);need(not p.is_absolute() and ".." not in p.parts and "\\" not in n and ":" not in n and p.as_posix()==n,"safe path")
  f=root/n;f.parent.mkdir(parents=True,exist_ok=True)
  with f.open("xb") as z:z.write(b)
def patch_for(name,old,new):
 # Git-compatible byte-preserving unified patch. Include explicit EOF markers
 # for inputs without final LF. All payload files are UTF-8 text.
 new.decode("utf-8")
 if old is not None:old.decode("utf-8")
 need(b"\0" not in new and (old is None or b"\0" not in old),"text only")
 a=old if old is not None else b""
 if old is None:
  head=f"diff --git a/{name} b/{name}\nnew file mode 100644\nindex 0000000..{blob(new)}\n".encode()
 else:
  head=f"diff --git a/{name} b/{name}\nindex {blob(old)}..{blob(new)} 100644\n".encode()
 # Split on LF only; preserve a literal CR, if present.
 def lines(b):
  q=b.split(b"\n");return [x+b"\n" for x in q[:-1]]+([q[-1]] if q[-1] else [])
 diff=difflib.diff_bytes(difflib.unified_diff,lines(a),lines(new),fromfile=(b"/dev/null" if old is None else ("a/"+name).encode()),tofile=("b/"+name).encode(),lineterm=b"\n")
 out=[head]
 for line in diff:
  out.append(line if line.endswith(b"\n") else line+b"\n\\ No newline at end of file\n")
 need(len(out)>1,"nonempty diff "+name)
 return b"".join(out)
def build(root,repo,out):
 env={**os.environ,"GIT_NO_LAZY_FETCH":"1","GIT_ALLOW_PROTOCOL":"","GIT_TERMINAL_PROMPT":"0","GIT_CONFIG_NOSYSTEM":"1","GIT_CONFIG_GLOBAL":os.devnull}
 def git(*a,cwd=None):
  return subprocess.check_output(["git","--no-optional-locks",*a],cwd=cwd,env=env,timeout=30,stderr=subprocess.STDOUT)
 need(git("-C",str(repo),"rev-parse",BASE+"^{commit}").decode().strip()==BASE,"verified Git baseline")
 r21=root/"L12_SUCCESSOR_PROFILE_R21_20261126"/"candidate"
 r20=root/"L12_FONT_PROFILE_R20_20261126"/"candidate"
 r16=root/"L12_STATIC_CANDIDATE_R16_20261126"/"bundle"
 r14=root/"L12_NEXT_PARITY_R14_20261126"/"candidate"
 profile_raw=checked(r21/"PROFILE_DRAFT.json",PROFILE);profile=json.loads(profile_raw)
 need(profile["status"]=="PROPOSED_NOT_ADMITTED" and profile["base"]==BASE and not profile["release_approval"] and not any(profile["authority"].values()),"review only")
 static=read(r20/"static");nxt=read(r20/"next");parent=read(r16/"parent")
 need(len(parent)==116 and digest(parent)==PARENT,"parent payload")
 need(len(static)==136 and digest(static)==PAYLOAD,"candidate payload")
 for files,key in ((static,"static_files"),(nxt,"next_files")):
  need(set(files)==set(profile[key]),"exact inventory "+key)
  for n,b in files.items():need(sha(b)==profile[key][n]["sha256"] and len(b)==profile[key][n]["bytes"],"pin "+n)
 delta=set(profile["static_replacements"])|set(profile["static_additions"])
 need(delta=={n for n,b in static.items() if parent.get(n)!=b} and len(delta)==22,"static delta")
 files={**{"deploy/live/"+n:static[n] for n in sorted(delta)},**nxt}
 tree={}
 for row in git("-C",str(repo),"ls-tree","-r",BASE).decode().splitlines():
  meta,n=row.split("\t",1);mode,typ,oid=meta.split()
  if typ=="blob":tree[n]=(mode,oid)
 replacements={"deploy/live/phuket-universe.html","deploy/live/en/phuket-universe.html","components/PhuketUniverse.tsx"}
 need(len(files)==45 and set(files)&set(tree)==replacements,"exact 45-file scope")
 old={"deploy/live/"+n:parent[n] for n in profile["static_replacements"]}
 r14_profile=json.loads(checked(r14/"NEXT_DRAFT.json",R14))
 old["components/PhuketUniverse.tsx"]=(r14/"inputs"/"components"/"PhuketUniverse.tsx").read_bytes()
 need(set(old)==replacements and all(tree[n]==("100644",blob(b)) for n,b in old.items()),"exact three Git preimages")
 need(r14_profile["input_blobs"]["components/PhuketUniverse.tsx"]==blob(old["components/PhuketUniverse.tsx"]),"component baseline")
 patch=b"".join(patch_for(n,old.get(n),b) for n,b in sorted(files.items()))
 need(len(patch)<600000,"lightweight patch bound")
 out.mkdir(parents=True,exist_ok=False)
 write(out,{"candidate.patch":patch,"PROFILE_DRAFT.json":profile_raw})
 work=out/"apply_check";work.mkdir();write(work,old)
 # One-time isolated scratch tree; no repo checkout or application writes.
 need(read(work)==old,"scratch baseline")
 args=["apply","--whitespace=nowarn"]
 git(*args,"--check",str(out/"candidate.patch"),cwd=work)
 git(*args,str(out/"candidate.patch"),cwd=work)
 need(read(work)==files,"45 exact postimages")
 git(*args,"--reverse","--check",str(out/"candidate.patch"),cwd=work)
 # Leave the actual applied review source in apply_check for direct inspection.
 # Reverse check is a validation, not a rollback or production operation.
 report={"scope":"R22_CONSOLIDATED_REVIEW_PATCH_ONLY","base":BASE,"profile_sha256":PROFILE,"candidate_payload_sha256":PAYLOAD,"patch_sha256":sha(patch),"patch_git_blob":blob(patch),"patch_bytes":len(patch),"files":{n:{"operation":"replace" if n in old else "add","old_git_blob":blob(old[n]) if n in old else None,"new_git_blob":blob(b),"sha256":sha(b),"bytes":len(b)} for n,b in sorted(files.items())},"checks":{"exact_three_preimages":True,"git_apply_check":True,"actual_isolated_apply":True,"all_45_postimages_exact":True,"git_reverse_check":True},"release_approval":False,"limitations":"Patch is an inspectable source proposal. Do not apply to main or deploy: historical route/font rules and exact release admission still conflict, no new manifest, actual Next build, full preflight, visual/independent approval or deployment."}
 rb=(json.dumps(report,indent=2,sort_keys=True)+"\n").encode()
 write(out,{"PATCH_QA.json":rb})
 print("PATCH",len(files),"files",len(old),"replaced",len(files)-len(old),"added","bytes",len(patch),"sha256",sha(patch),"blob",blob(patch),flush=True)
 print("QA_SHA256",sha(rb),"QA_BLOB",blob(rb),"APPLIED",len(read(work)),flush=True)
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ("evidence-root","repo","output"):p.add_argument("--"+n,type=Path,required=True)
 a=p.parse_args();r=a.evidence_root.resolve();repo=a.repo.resolve();out=a.output.resolve()
 need(not out.exists() and out!=r and out!=repo and repo not in out.parents,"new output")
 build(r,repo,out)
if __name__=="__main__":main()
