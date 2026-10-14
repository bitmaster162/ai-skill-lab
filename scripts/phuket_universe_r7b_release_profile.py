"""R7B local-only sitemap freshness repair: independent SHA pins and exact R7 parent."""
from __future__ import annotations
import hashlib,json,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/"deploy/live"
RELEASE="PHUKET_UNIVERSE_U3_E38_DORMANT_R7B_20261015"
PREV_RELEASE="PHUKET_UNIVERSE_U3_E38_DORMANT_R7_20261015"
PREV_HEAD="8214125bbc1b90467ca24fe5e092898159a35828"
PREV_PROFILE_SHA="a0aad5ac8a819bd3ebe25d0c4656c211ced53befbe27e20255de81d6dfc64bc8"
PREV_MANIFEST_SHA="19b2e65f1199fc603a227980943d54d08fe02fd483095ffc5af4efa604fce305"
PREV_PAYLOAD_SHA="7b74fffcd33b11c8985c5b9bc67bbee30c2d59594495183d129ab44399ab64cb"
PROFILE_PATH=ROOT/"data/phuket_universe_u3_e38_r7b_profile.json"
PROFILE_SHA="4bb0b241618a3d75aee2de39ffd1771279e4d13399e00af2fa45661e57b26d39"
MANIFEST_SHA="a8166f8a45f17df8b7359dfb62bba467c6061f61cab1db164183216d31c42bb6"
PAYLOAD_SHA="bfe1742f1ce3946f700fff9a67d273d840809d33f5e279123a205696305d2cab"
PUBLIC_SITEMAP_DAY="2026-10-15"
AUTHORITY={"push":False,"pr":False,"merge":False,"deploy":False,"production":False,
           "scheduler":False,"real_listings":False,"d1_migration":False,
           "event_receiver":False,"universe_events_enabled":False}
BUDGETS={"payload_max_bytes":1362928,"nonfont_max_bytes":1241540,
         "font_max_bytes":121388,"font_max_file_bytes":55296,
         "html_max_file_bytes":38912,"css_max_file_bytes":41984}
def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def digest(rows:dict)->str:
 return sha("".join(f"{k}\t{v['size']}\t{v['sha256']}\n" for k,v in sorted(rows.items())).encode())
def need(ok,why):
 if not ok:raise ValueError(why)
def git_blob(ref,path)->bytes:
 p=subprocess.run(["git","-C",str(ROOT),"show",ref+":"+path],
                  capture_output=True,timeout=50)
 need(p.returncode==0,"Git reference unavailable: "+path)
 return p.stdout
def active()->bool:
 return json.loads((LIVE/"_release.json").read_text("utf-8")).get("release_id")==RELEASE

def profile()->dict:
 raw=PROFILE_PATH.read_bytes()
 need(sha(raw)==PROFILE_SHA,"R7B profile independently pinned SHA drift")
 p=json.loads(raw)
 need(p.get("schema")=="ai-skill-lab.release-profile.v1"
      and p.get("release_id")==RELEASE
      and p.get("previous_release_id")==PREV_RELEASE
      and p.get("previous_commit")==PREV_HEAD
      and p.get("previous_manifest_sha256")==PREV_MANIFEST_SHA
      and p.get("manifest_sha256")==MANIFEST_SHA
      and p.get("payload_sha256")==PAYLOAD_SHA
      and p.get("file_count")==107
      and p.get("public_routes")==56 and p.get("workshop_routes")==54
      and p.get("authority")==AUTHORITY and p.get("budgets")==BUDGETS
      and p.get("accepted_listings")==0
      and p.get("changed_r7_files")==["sitemap.xml"],
      "R7B identity/authority/scope drift")
 old=git_blob(PREV_HEAD,"data/phuket_universe_u3_e38_r7_profile.json")
 need(sha(old)==PREV_PROFILE_SHA,"R7 original reviewed profile changed")
 previous=json.loads(old)
 for key in ("r6_file_pins","r7_html_pins","r7_source_sha256","r3_file_pins",
             "r5_file_pins","parent_commit","parent_file_pins","parent_payload_sha256",
             "parent_manifest_sha256","parent_release_id","new_files","new_u2_files",
             "changed_r5_files","changed_r6_files","new_u3_files",
             "transfer_profiles","fonts","u3_universe_events","policy_sha256",
             "source_report_sha256","input_sha256"):
  need(p.get(key)==previous.get(key),"R7 historical lineage changed: "+key)
 need(len(p["r7_file_pins"])==107 and digest(p["r7_file_pins"])==PREV_PAYLOAD_SHA,
      "R7 independently pinned asset bytes altered")
 need(set(p.get("source_override_sha256",{}))==set(previous["source_override_sha256"]),
      "R7 source pin universe changed")
 need(set(p.get("r7b_source_sha256",{}))=={
       "app/sitemap.ts","scripts/build_phuket_universe_r7b.py",
       "scripts/test_phuket_universe_r7b.py"},"R7B exact new source scope")
 return p

def verify_integrity()->dict:
 p=profile()
 raw=(LIVE/"_release.json").read_bytes()
 need(sha(raw)==MANIFEST_SHA,"R7B manifest SHA drift")
 m=json.loads(raw);rows=m.get("files",[])
 need(m.get("schema")=="ai-skill-lab.static-release.v1"
      and m.get("release_id")==RELEASE and m.get("file_count")==107
      and len(rows)==107 and len({x["path"] for x in rows})==107,
      "R7B manifest identity/duplication")
 observed={}
 for file in LIVE.rglob("*"):
  need(not file.is_symlink(),"R7B symlink denied")
  if file.is_file() and file.name!="_release.json":
   raw=file.read_bytes()
   observed[file.relative_to(LIVE).as_posix()]={"size":len(raw),"sha256":sha(raw)}
 indexed={x["path"]:{"size":x["size"],"sha256":x["sha256"]} for x in rows}
 need(observed==indexed and digest(observed)==PAYLOAD_SHA and m.get("payload_sha256")==PAYLOAD_SHA,
      "R7B actual content/manifest mismatch")
 prev=p["r7_file_pins"]
 need(set(observed)==set(prev)
      and {n for n in prev if observed[n]!=prev[n]}=={"sitemap.xml"},
      "R7B must modify only sitemap.xml inherited payload")
 need(sum(x["size"] for x in observed.values())==BUDGETS["payload_max_bytes"],
      "R7B payload size drift")
 for n in p["r7_html_pins"]:
  need(observed[n]==p["r7_html_pins"][n],"R7B public page changed vs R7")
 need((LIVE/"phuket-universe-events.js").read_bytes()==git_blob(PREV_HEAD,"deploy/live/phuket-universe-events.js"),
      "R7B client event script changed")
 need(b"const ENABLED = false;" in (LIVE/"phuket-universe-events.js").read_bytes(),
      "R7B event authority enabled")
 xml=(LIVE/"sitemap.xml").read_text("utf-8")
 need(xml.count("<lastmod>"+PUBLIC_SITEMAP_DAY+"</lastmod>")==56
      and xml.count("<lastmod>")==56,"R7B sitemap lastmod coverage")
 return {"release":RELEASE,"files":107,"routes":56,"workshop_routes":54,
         "r7_payload_unchanged":106,"payload_bytes":1362928,
         "real_listings":0,"events_enabled":False,"sitemap_date":PUBLIC_SITEMAP_DAY}

def legacy_r6_html(rel: str) -> bytes:
    """Reconstruct exact R6 bytes only for 56 approved R7/R7B HTML changes.

    R7B must be SHA-bound to R7, R7 must be SHA-bound to R6. This does not
    exempt new content: the exact additive transformation is verified.
    """
    p=profile()
    need(rel in p["changed_r6_files"] and rel.endswith(".html"),
         "R7B legacy parity escape outside 56 approved pages")
    old=git_blob("3d58999a382b2c11eae7da3d97e9e650c1326f46","deploy/live/"+rel)
    old_pin=p["r6_file_pins"][rel]
    need(len(old)==old_pin["size"] and sha(old)==old_pin["sha256"],
         "R7B immutable R6 page hash drift")
    r7=git_blob(PREV_HEAD,"deploy/live/"+rel)
    r7_pin=p["r7_html_pins"][rel]
    need(len(r7)==r7_pin["size"] and sha(r7)==r7_pin["sha256"],
         "R7B immutable R7 page hash drift")
    current=(LIVE/rel).read_bytes()
    need(current==r7,"R7B changed public HTML since R7")
    from build_phuket_universe_r7 import make_page
    need(make_page(rel,old.decode("utf-8")).encode("utf-8")==current,
         "R7B page cannot be reconstructed from pinned R6")
    return old

def check_release()->dict:
 status=verify_integrity()
 from build_phuket_universe_r7b import render
 expected=render()
 actual={file.relative_to(LIVE).as_posix():file.read_bytes()
         for file in LIVE.rglob("*") if file.is_file()}
 need(expected==actual,"R7B reproducibility failure")
 p=profile()
 for name,expected_sha in p["source_override_sha256"].items():
  need((ROOT/name).is_file() and sha((ROOT/name).read_bytes())==expected_sha,
       "R7B source SHA mismatch: "+name)
 for name,expected_sha in p["r7b_source_sha256"].items():
  need(sha((ROOT/name).read_bytes())==expected_sha,"R7B newly pinned source mismatch: "+name)
 source=(ROOT/"app/sitemap.ts").read_text("utf-8")
 need(source.count('const lastModified = "2026-10-15";')==1
      and source.count('lastModified: universeRoutes.includes(route) ? "2026-10-15" : lastModified')==1,
      "R7B source sitemap lastmod parity")
 for file in ("schema/public_event_daily_e38.sql","services/lead-ingress/api/event.js",
              "services/lead-receiver-cloudflare/src/index.js",
              "services/lead-receiver-cloudflare/wrangler.jsonc","package-lock.json","package.json"):
  need((ROOT/file).read_bytes()==git_blob(PREV_HEAD,file),
       "R7B prohibited schema/ingress/dependency mutation: "+file)
 return status
