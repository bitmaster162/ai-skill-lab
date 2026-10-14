#!/usr/bin/env python3
"""R7 local deterministic builder from pinned R6 Git parent and fixed U3 design.

Read-only by default. Prepare-local may write only reviewed R7 payload to this
isolated worktree's deploy/live after verifying a bit-identical R6 baseline.
No network, secret, Cloudflare, Scheduler, Git remote, or Vercel side effect.
"""
from __future__ import annotations
import argparse, hashlib, io, json, subprocess, sys, tarfile
from pathlib import Path, PurePosixPath

ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/"deploy/live"
RELEASE="PHUKET_UNIVERSE_U3_E38_DORMANT_R7_20261015"
R6_COMMIT="3d58999a382b2c11eae7da3d97e9e650c1326f46"
R6_TREE="34fc913502977cf7a825791725fd8fa97ac93e86"
R6_MANIFEST="5d07745a1220b1da82e224409210635ae83511f6184101671ea24987468b5966"
R7_BRANCH="agent/phuket-universe-u3-r7-static-integration-local-r1"
SRC=ROOT/"tools/phuket_universe_u3"
sys.path.insert(0,str(SRC))
from preview import make_page, sha  # source committed in R7

def need(condition:bool,message:str)->None:
    if not condition:raise ValueError(message)

def git(*args):
    run=subprocess.run(["git","-C",str(ROOT),*args],capture_output=True,timeout=50)
    need(run.returncode==0,"Git read failed "+args[0])
    return run.stdout

def r6_parent()->dict[str,bytes]:
    need(git("rev-parse",R6_COMMIT+"^{tree}").decode().strip()==R6_TREE,"R6 base tree drift")
    files={}
    with tarfile.open(fileobj=io.BytesIO(git("archive","--format=tar",R6_COMMIT,"deploy/live"))) as tar:
        for info in tar:
            if info.isdir():continue
            need(info.isfile() and info.name.startswith("deploy/live/"),"nonfile tar entry")
            name=info.name.removeprefix("deploy/live/")
            need(name and name not in files and ".." not in PurePosixPath(name).parts and "\\" not in name,"unsafe archive path")
            f=tar.extractfile(info)
            need(f is not None,"tar content missing")
            files[name]=f.read()
    need(len(files)==107 and sha(files["_release.json"])==R6_MANIFEST,"R6 manifest/files changed")
    m=json.loads(files["_release.json"])
    need(m["file_count"]==106 and m["release_id"]=="PHUKET_UNIVERSE_U2_EMPTY_CATALOG_R6_20261014","R6 release mismatch")
    recorded={}
    for x in m["files"]:
        raw=files[x["path"]]
        need(len(raw)==x["size"] and sha(raw)==x["sha256"],"R6 payload drift "+x["path"])
        need(x["path"] not in recorded,"duplicate R6 file")
        recorded[x["path"]]=x
    need(set(files)==set(recorded)|{"_release.json"},"R6 undeclared file")
    return files

def render()->dict[str,bytes]:
    files=r6_parent()
    html=sorted(k for k in files if k.endswith(".html") and k!="404.html")
    need(len(html)==56,"R7 route scope")
    for rel in html:
        files[rel]=make_page(rel,files[rel].decode("utf-8")).encode("utf-8")
    need("phuket-universe-events.js" not in files,"R6 event asset already exists")
    script=(ROOT/"public/phuket-universe-events.js").read_bytes()
    need(b"const ENABLED = false" in script and b'credentials: "omit"' in script,"event unexpectedly enabled")
    files["phuket-universe-events.js"]=script
    rows=[{"path":name,"size":len(data),"sha256":sha(data)}
          for name,data in sorted(files.items()) if name!="_release.json"]
    need(len(rows)==107,"R7 unexpected inventory")
    payload=sha("".join(f"{x['path']}\t{x['size']}\t{x['sha256']}\n" for x in rows).encode())
    m={"schema":"ai-skill-lab.static-release.v1","release_id":RELEASE,
       "file_count":len(rows),"payload_sha256":payload,"files":rows}
    files["_release.json"]=(json.dumps(m,indent=2,sort_keys=True)+"\n").encode("utf-8")
    return files

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-local",action="store_true")
    args=parser.parse_args()
    files=render()
    if args.prepare_local:
        need(git("branch","--show-current").decode().strip()==R7_BRANCH,"Wrong R7 branch")
        original=r6_parent()
        live_files={p.relative_to(LIVE).as_posix():p.read_bytes() for p in LIVE.rglob("*") if p.is_file()}
        need(not any(p.is_symlink() for p in LIVE.rglob("*")),"Symlink in live")
        need(live_files==original,"R6 local baseline not pristine")
        need(not git("diff","--name-only","--","deploy/live").strip(),"Staged live diff")
        for name,data in sorted(files.items(),key=lambda x:x[0]=="_release.json"):
            target=LIVE/name
            need(target.resolve().is_relative_to(LIVE.resolve()) and not target.is_symlink(),"Unsafe local write")
            if target.exists():
                if target.read_bytes()!=data:target.write_bytes(data)
            else:
                with target.open("xb") as f:f.write(data)
    observed={p.relative_to(LIVE).as_posix():p.read_bytes() for p in LIVE.rglob("*") if p.is_file()}
    if args.prepare_local:need(observed==files,"Local R7 write/readback mismatch")
    m=json.loads(files["_release.json"])
    print(json.dumps({"release":RELEASE,"files":len(files)-1,"manifest_sha256":sha(files["_release.json"]),
        "payload_sha256":m["payload_sha256"],"payload_bytes":sum(len(b) for k,b in files.items() if k!="_release.json"),
        "prepared":bool(args.prepare_local),"authority":{"push":False,"merge":False,"deploy":False,
        "d1":False,"events_enabled":False}},sort_keys=True),flush=True)
if __name__=="__main__":main()
