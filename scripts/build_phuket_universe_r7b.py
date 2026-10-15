#!/usr/bin/env python3
"""Local-only R7B freshness repair. Immutable R7 remains in previous Git commit."""
from __future__ import annotations
import argparse,hashlib,io,json,subprocess,tarfile
from pathlib import Path,PurePosixPath

ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/"deploy/live"
R7_HEAD="8214125bbc1b90467ca24fe5e092898159a35828"
R7_TREE="5ab963e29c45d99b7532093a24affdf2d93c44ce"
R7_MANIFEST="19b2e65f1199fc603a227980943d54d08fe02fd483095ffc5af4efa604fce305"
R7B_BRANCH="agent/phuket-universe-u3-r7b-freshness-local-r1"
RELEASE="PHUKET_UNIVERSE_U3_E38_DORMANT_R7B_20261015"
DATE="2026-10-15"
def need(x,msg):
 if not x:raise ValueError(msg)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def git(*args):
 p=subprocess.run(["git","-C",str(ROOT),*args],capture_output=True,timeout=50)
 need(p.returncode==0,"Git read failed "+args[0]);return p.stdout

def r7_parent():
 need(git("rev-parse",R7_HEAD+"^{tree}").decode().strip()==R7_TREE,"R7 Git tree drift")
 files={}
 with tarfile.open(fileobj=io.BytesIO(git("archive","--format=tar",R7_HEAD,"deploy/live"))) as archive:
  for item in archive:
   if item.isdir():continue
   need(item.isfile() and item.name.startswith("deploy/live/"),"Unexpected R7 archive type")
   name=item.name.removeprefix("deploy/live/")
   need(name and name not in files and ".." not in PurePosixPath(name).parts and "\\" not in name,"Unsafe R7 archive name")
   content=archive.extractfile(item)
   need(content is not None,"R7 content missing")
   files[name]=content.read()
 need(len(files)==108 and sha(files["_release.json"])==R7_MANIFEST,"R7 manifest/size drift")
 m=json.loads(files["_release.json"])
 need(m["file_count"]==107 and m["release_id"]=="PHUKET_UNIVERSE_U3_E38_DORMANT_R7_20261015","R7 identity drift")
 assert set(files)=={x["path"] for x in m["files"]}|{"_release.json"}
 for x in m["files"]:
  data=files[x["path"]]
  need(len(data)==x["size"] and sha(data)==x["sha256"],"R7 source file drift "+x["path"])
 return files

def render():
 files=r7_parent()
 xml=files["sitemap.xml"].decode("utf-8")
 need(xml.count("<lastmod>2026-10-11</lastmod>")==54,"R7 workshop freshness authority")
 need(xml.count("<lastmod>2026-10-14</lastmod>")==2,"R7 Universe freshness authority")
 need(xml.count("<lastmod>")==56,"R7 sitemap route count")
 xml=xml.replace("<lastmod>2026-10-11</lastmod>",f"<lastmod>{DATE}</lastmod>")
 xml=xml.replace("<lastmod>2026-10-14</lastmod>",f"<lastmod>{DATE}</lastmod>")
 need(xml.count(f"<lastmod>{DATE}</lastmod>")==56,"R7B freshness coverage")
 files["sitemap.xml"]=xml.encode("utf-8")
 rows=[{"path":k,"size":len(v),"sha256":sha(v)} for k,v in sorted(files.items()) if k!="_release.json"]
 payload=sha("".join(f"{x['path']}\t{x['size']}\t{x['sha256']}\n" for x in rows).encode())
 m={"schema":"ai-skill-lab.static-release.v1","release_id":RELEASE,
    "file_count":107,"payload_sha256":payload,"files":rows}
 files["_release.json"]=(json.dumps(m,sort_keys=True,indent=2)+"\n").encode("utf-8")
 need(len(files)==108 and len(rows)==107,"R7B manifest inventory")
 return files

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--prepare-local",action="store_true")
 args=parser.parse_args()
 files=render()
 if args.prepare_local:
  need(git("branch","--show-current").decode().strip()==R7B_BRANCH,"R7B branch guard")
  actual={p.relative_to(LIVE).as_posix():p.read_bytes() for p in LIVE.rglob("*") if p.is_file()}
  need(actual==r7_parent() and not any(p.is_symlink() for p in LIVE.rglob("*")),"R7 live parent not exact")
  for name in ["sitemap.xml","_release.json"]:
   need((LIVE/name).is_file() and not(LIVE/name).is_symlink(),"R7B write target invalid")
   (LIVE/name).write_bytes(files[name])
  now={p.relative_to(LIVE).as_posix():p.read_bytes() for p in LIVE.rglob("*") if p.is_file()}
  need(now==files,"R7B write readback changed")
 m=json.loads(files["_release.json"])
 print(json.dumps({"release":RELEASE,"manifest_sha256":sha(files["_release.json"]),
   "payload_sha256":m["payload_sha256"],"file_count":m["file_count"],
   "payload_bytes":sum(len(v) for k,v in files.items() if k!="_release.json"),
   "r7_preserved_files":106,"date":DATE,"prepared":args.prepare_local,
   "authority":{"push":False,"pr":False,"merge":False,"deploy":False,"d1":False}},sort_keys=True),flush=True)
if __name__=="__main__":main()
