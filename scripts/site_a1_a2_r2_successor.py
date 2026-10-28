#!/usr/bin/env python3
"""Single exact SITE-A1/A2 R2 successor; R7B historic rules remain untouched."""
from __future__ import annotations
import hashlib,json,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/"deploy/live"
RELEASE="PHUKET_UNIVERSE_U3_E38_DORMANT_R7B_20261015"
PATCH="SITE_A1_A2_R2_20261026_DRAFT_REVIEW"
MANIFEST_SHA="f8cdc7b27aca6ea5815c8237a97acf53a5c7ef9f9db24d4ff19e6c5ae9c5ec53"
PAYLOAD_SHA="1393d778de86ba69b0a187f545d1aa606ef3ccf0d89f189cc0be75ec21e9fcca"
ADMISSION="data/SITE_A1_A2_R2_METADATA_SUCCESSOR_ADMISSION_V2_20261026.json"
ADMISSION_SHA="279ee064f8a93f25af5ca6b64362bd6f16d6a048a74fd611977c8585f76ff1ef"
SOURCE_COMMIT="9d2ed0c1fa98d94457052392208cb3526385a2ba"
SOURCE_TREE="96a3619cd476d4174f6fff016fdfa3945fe7cc58"
BASE="d0a858a7787088dabf6d914e45fb0cde41b743e8"
CHAIN=(
 ("907c24662de5b6360f210324a13a0c2e2d309f21","a8166f8a45f17df8b7359dfb62bba467c6061f61cab1db164183216d31c42bb6",None),
 ("d1b0d94744b2768b8bc39301b5e10cbf49fa7258","b10b2ad45184e2f19a329dbe22b7e2c18fef0c075f13a31a435abdf83167adc3","a8166f8a45f17df8b7359dfb62bba467c6061f61cab1db164183216d31c42bb6"),
 ("cae4b9e319a395512639dffdb09a897d215c0181","c9c1ffa4a227a4ed324901c7bb6019e16dcf28722fc70c72e70badfb22752505","b10b2ad45184e2f19a329dbe22b7e2c18fef0c075f13a31a435abdf83167adc3"),
 ("d20802cf9d13d9c7e9a9f3f113b7852acf97d164","fc57c61c7ac502644665f7cc06152f43fb0b5d7f67827eb6fd4b12aadfc83f37","c9c1ffa4a227a4ed324901c7bb6019e16dcf28722fc70c72e70badfb22752505"),
 ("74095414ea1fa3f41b879ebfa9b55fd525242d2a","6159de33768a88d9d945fc3fc2cbfde194cc2cf087783acb63b65acaabcffc56","fc57c61c7ac502644665f7cc06152f43fb0b5d7f67827eb6fd4b12aadfc83f37"),
 (SOURCE_COMMIT,"ad8282f6b7a670c9e5e5f840dd0d427f3c24f87a2210f64d40dab1cf7bf497e5","6159de33768a88d9d945fc3fc2cbfde194cc2cf087783acb63b65acaabcffc56"),
)
STATIC_DELTA=frozenset({"sitemap.xml","start.html"})
HISTORIC_FILES=(
 "scripts/phuket_universe_r7b_release_profile.py",
 "data/phuket_universe_u3_e38_r7b_profile.json",
 "scripts/test_phuket_universe_r7b.py",
 "scripts/test_phuket_universe_r7b_ci_fetch_depth.py",
)

class SuccessorHold(ValueError):pass
def must(value,reason):
 if not value:raise SuccessorHold("SITE_A1_A2_R2_STOP:"+reason)
def sha(raw:bytes)->str:return hashlib.sha256(raw).hexdigest()
def run_git(*args)->bytes:
 p=subprocess.run(["git","--no-optional-locks","-C",str(ROOT),*args],
     check=False,capture_output=True,timeout=50)
 must(p.returncode==0,"GIT:"+repr(args))
 return p.stdout
def git_blob(commit,path):
 return run_git("show",commit+":"+path)
def active()->bool:
 try:
  m=json.loads((LIVE/"_release.json").read_bytes())
  return m.get("release_id")==RELEASE and m.get("patch_id")==PATCH
 except (ValueError,OSError,TypeError):return False
def digest_rows(rows):
 return sha("".join(f"{r['path']}\t{r['size']}\t{r['sha256']}\n" for r in sorted(rows,key=lambda x:x["path"])).encode())
def ancestor_chain(drop_ancestor=None, historical_override=None):
 """Read immutable git objects; no production network or mutation."""
 must(run_git("show","-s","--format=%T",SOURCE_COMMIT).decode().strip()==SOURCE_TREE,"R2_COMMIT_TREE")
 must(run_git("merge-base","--is-ancestor",SOURCE_COMMIT,"HEAD")==b"","R2_NOT_ANCESTOR")
 must(run_git("merge-base","--is-ancestor",BASE,SOURCE_COMMIT)==b"","BASE_NOT_ANCESTOR")
 expected=[(c,s,p) for c,s,p in CHAIN if c!=drop_ancestor]
 must(len(expected)==len(CHAIN),"CHAIN_MISSING_ANCESTOR")
 prior=None
 records=[]
 for commit,want,parent in expected:
  historical=git_blob(commit,"deploy/live/_release.json")
  if commit==CHAIN[0][0] and historical_override is not None:historical=historical_override
  must(sha(historical)==want,"HISTORIC_MANIFEST_SHA:"+commit[:10])
  value=json.loads(historical)
  must(value.get("parent_manifest_sha256")==parent,"PARENT_POINTER:"+commit[:10])
  if prior is not None:must(parent==prior,"CHAIN_BREAK:"+commit[:10])
  must(run_git("merge-base","--is-ancestor",commit,SOURCE_COMMIT)==b"","NOT_ANCESTOR:"+commit[:10])
  records.append((commit,want))
  prior=want
 # Preserve each historical seal script and profile from original pinned base.
 for path in HISTORIC_FILES:
  must(git_blob("HEAD",path)==git_blob(BASE,path) and not run_git("diff","--name-only","--",path).strip(),"HISTORIC_RULE_CHANGED:"+path)
 r7b=git_blob(CHAIN[0][0],"deploy/live/_release.json")
 historic=json.loads(r7b)
 must(historic["release_id"]==RELEASE and historic["file_count"]==107
      and historic["payload_sha256"]=="bfe1742f1ce3946f700fff9a67d273d840809d33f5e279123a205696305d2cab","HISTORIC_R7B_RELEASE")
 must(sha(git_blob(CHAIN[0][0],"data/phuket_universe_u3_e38_r7b_profile.json"))=="4bb0b241618a3d75aee2de39ffd1771279e4d13399e00af2fa45661e57b26d39","HISTORIC_R7B_PROFILE")
 return records

def verify(manifest_override:bytes|None=None,extra_file:str|None=None,
           drop_ancestor:str|None=None,historical_override:bytes|None=None)->dict:
 must(active() if manifest_override is None else True,"NO_SUCCESSOR_AUTHORITY")
 actual_bytes=(LIVE/"_release.json").read_bytes() if manifest_override is None else manifest_override
 must(sha(actual_bytes)==MANIFEST_SHA,"SUCCESSOR_MANIFEST_SHA")
 m=json.loads(actual_bytes)
 must(m.get("release_id")==RELEASE and m.get("patch_id")==PATCH
      and m.get("parent_manifest_sha256")==CHAIN[-1][1]
      and m.get("file_count")==108 and m.get("payload_sha256")==PAYLOAD_SHA,
      "SUCCESSOR_IDENTITY")
 rows=m.get("files")
 must(isinstance(rows,list) and len(rows)==108 and len({x["path"] for x in rows})==108,"FILES_LENGTH")
 must(digest_rows(rows)==PAYLOAD_SHA,"PAYLOAD_DIGEST")
 observed={}
 for path in LIVE.rglob("*"):
  must(not path.is_symlink(),"SYMLINK")
  if path.is_file() and path.name!="_release.json":
   raw=path.read_bytes()
   observed[path.relative_to(LIVE).as_posix()]={"size":len(raw),"sha256":sha(raw)}
 if extra_file:observed[extra_file]={"size":0,"sha256":sha(b"")}
 recorded={x["path"]:{"size":x["size"],"sha256":x["sha256"]} for x in rows}
 must(observed==recorded,"ACTUAL_ASSET_MISMATCH")
 prior=json.loads(git_blob(CHAIN[-1][0],"deploy/live/_release.json"))
 parent_index={x["path"]:(x["size"],x["sha256"]) for x in prior["files"]}
 changes={p for p in recorded if (recorded[p]["size"],recorded[p]["sha256"])!=parent_index[p]}
 must(changes==STATIC_DELTA and set(recorded)==set(parent_index),"EXACT_CHANGED_STATIC_FILES")
 # The previous R2 safeguard is permanent lineage evidence, never overwritten.
 r2_admission_name="data/SITE_A1_A2_R2_SUCCESSOR_ADMISSION_CANDIDATE_20261026.json"
 r2_admission_bytes=git_blob(SOURCE_COMMIT,r2_admission_name)
 must(sha(r2_admission_bytes)=="247c46cf0f8f72a019525294f803ba58028cd7b8869253170add2fce73e20564",
      "ORIGINAL_R2_ADMISSION_HASH")
 r2=json.loads(r2_admission_bytes)
 must(r2.get("candidate_manifest_sha256")==CHAIN[-1][1]
      and r2.get("changed_files_count")==28,"ORIGINAL_R2_ADMISSION")
 oldpins=r2["changed_files_relative_to_existing_pr_head"]
 must(len(oldpins)==28,"OLD_R2_FILES")
 for name,entry in oldpins.items():
  blob=git_blob(SOURCE_COMMIT,name)
  must(sha(blob)==entry["sha256"] and len(blob)==entry["size"],"ORIGINAL_R2_PIN:"+name)
 must(set(oldpins)==set(run_git("diff","--name-only",CHAIN[-2][0],SOURCE_COMMIT).decode().splitlines())-{r2_admission_name},
      "ORIGINAL_R2_FILESET")
 must(sha((ROOT/ADMISSION).read_bytes())==ADMISSION_SHA,"METADATA_ADMISSION_HASH")
 adm=json.loads((ROOT/ADMISSION).read_bytes())
 must(adm.get("candidate_manifest_sha256")==MANIFEST_SHA and
      adm.get("candidate_payload_sha256")==PAYLOAD_SHA and
      adm.get("source_r2_manifest_sha256")==CHAIN[-1][1] and
      adm.get("candidate_manifest_parent_sha256")==CHAIN[-1][1] and
      adm.get("patch_id")==PATCH and
      adm.get("source_commit_sha")==SOURCE_COMMIT and
      adm.get("historical_r7b_manifest_sha256")==CHAIN[0][1],"METADATA_ADMISSION_IDENTITY")
 expected_files={
  "app/sitemap.ts","components/workshop/WorkshopStart.tsx",
  "data/SITE_A1_A2_R2_METADATA_SUCCESSOR_ADMISSION_V2_20261026.json",
  "deploy/live/_release.json","deploy/live/sitemap.xml","deploy/live/start.html",
  "scripts/check_phuket_release_r3.py","scripts/check_search_metadata.py",
  "scripts/phuket_release_profile.py","scripts/site_a1_a2_r2_successor.py",
  "scripts/test_site_a1_a2_r2_successor.py","scripts/test_site_a2_metadata_gate.py"}
 must(set(adm.get("files_exact",[]))==expected_files,"METADATA_EXACT_FILE_SCOPE")
 for name,entry in adm.get("sha_pins_non_recursive",{}).items():
  raw=(ROOT/name).read_bytes()
  must(sha(raw)==entry["sha256"] and len(raw)==entry["bytes"],"METADATA_PIN:"+name)
 must(set(adm.get("sha_pins_non_recursive",{}))==
      {"app/sitemap.ts","components/workshop/WorkshopStart.tsx","deploy/live/_release.json","deploy/live/sitemap.xml","deploy/live/start.html",
       "scripts/check_search_metadata.py"},"METADATA_PIN_SET")
 must(set(adm.get("exact_2026_10_26_ru_routes",[]))==
      {"/business","/challenge","/faq","/phuket","/privacy",
       "/projects","/proof","/studio","/teens","/terms"},"RU_DATE_ROUTES")
 must(adm.get("exact_2026_10_28_ru_start_route")=="/start","RU_START_28")
 must(set(adm.get("exact_2026_10_26_bilingual_pricing_routes",[]))==
      {"/pricing","/en/pricing"},"PRICE_DATE_ROUTES")

 chain=ancestor_chain(drop_ancestor,historical_override)
 return {"status":"SITE_A1_A2_R2_SUCCESSOR_PASS","release_id":RELEASE,"patch_id":PATCH,
         "manifest_sha256":MANIFEST_SHA,"payload_sha256":PAYLOAD_SHA,
         "source_commit":SOURCE_COMMIT,"r7b_immutable_ancestors":len(chain),
         "static_assets":108,"modified_vs_r2":sorted(changes),"production_authority":False}
def inherited_pin_overrides()->dict[str,str]:
 verified=verify()
 m=json.loads((LIVE/"_release.json").read_bytes())
 old=json.loads(git_blob(CHAIN[0][0],"deploy/live/_release.json"))
 prior={x["path"]:(x["size"],x["sha256"]) for x in old["files"]}
 return {"deploy/live/"+x["path"]:x["sha256"] for x in m["files"]
         if x["path"] not in prior or (x["size"],x["sha256"])!=prior[x["path"]]}
if __name__=="__main__":
 print(json.dumps(verify(),sort_keys=True))
