"""Pin exact U3 R7 release; preserve R6 and all E3.8 production boundaries.

Read-only qualification. Does not grant push, PR, merge, deploy or D1 authority.
"""
from __future__ import annotations
import hashlib,json,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/"deploy/live"
RELEASE="PHUKET_UNIVERSE_U3_E38_DORMANT_R7_20261015"
PROFILE_PATH=ROOT/"data/phuket_universe_u3_e38_r7_profile.json"
PROFILE_SHA="a0aad5ac8a819bd3ebe25d0c4656c211ced53befbe27e20255de81d6dfc64bc8"
MANIFEST_SHA="19b2e65f1199fc603a227980943d54d08fe02fd483095ffc5af4efa604fce305"
PAYLOAD_SHA="7b74fffcd33b11c8985c5b9bc67bbee30c2d59594495183d129ab44399ab64cb"
R6_PROFILE_SHA="1a407c61ff201fca79037779af18e40774ad01d32a0525e3160e060f1b859be4"
R6_MANIFEST_SHA="5d07745a1220b1da82e224409210635ae83511f6184101671ea24987468b5966"
R6_PAYLOAD_SHA="0b5f3b9d20d3dbcb9dcb03c6e65c0f9b513792c7cbaf71d958ee15d13914ec94"
R6_HEAD="3d58999a382b2c11eae7da3d97e9e650c1326f46"
PAGES=frozenset({"phuket-universe.html","en/phuket-universe.html"})
NEW_FILE=frozenset({"phuket-universe-events.js"})
AUTHORITY={"push":False,"pr":False,"merge":False,"deploy":False,"production":False,
           "scheduler":False,"real_listings":False,"d1_migration":False,
           "event_receiver":False,"universe_events_enabled":False}
BUDGETS={"payload_max_bytes":1362928,"nonfont_max_bytes":1241540,
         "font_max_bytes":121388,"font_max_file_bytes":55296,
         "html_max_file_bytes":38912,"css_max_file_bytes":41984}
EVENTS=frozenset({"universe_click","project_click","listing_click"})

def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def digest(rows:dict)->str:
    return sha("".join(f"{k}\t{v['size']}\t{v['sha256']}\n" for k,v in sorted(rows.items())).encode())
def require(cond:bool,message:str):
    if not cond:raise ValueError(message)

def active()->bool:
    return json.loads((LIVE/"_release.json").read_text(encoding="utf-8")).get("release_id")==RELEASE

def profile()->dict:
    raw=PROFILE_PATH.read_bytes()
    require(sha(raw)==PROFILE_SHA,"R7 reviewed profile SHA drift")
    p=json.loads(raw)
    assert p["release_id"]==RELEASE
    require(p.get("schema")=="ai-skill-lab.release-profile.v1"
        and p.get("manifest_sha256")==MANIFEST_SHA
        and p.get("payload_sha256")==PAYLOAD_SHA
        and p.get("file_count")==107
        and p.get("public_routes")==56 and p.get("workshop_routes")==54
        and p.get("previous_release_id")=="PHUKET_UNIVERSE_U2_EMPTY_CATALOG_R6_20261014"
        and p.get("previous_commit")==R6_HEAD
        and p.get("previous_manifest_sha256")==R6_MANIFEST_SHA
        and p.get("authority")==AUTHORITY and p.get("budgets")==BUDGETS
        and p.get("accepted_listings")==0
        and set(p.get("new_u3_files",[]))==NEW_FILE
        and set(p.get("u3_universe_events",[]))==EVENTS,
        "R7 identity/authority/budget drift")
    old_raw=(ROOT/"data/phuket_housing_r6_profile.json").read_bytes()
    require(sha(old_raw)==R6_PROFILE_SHA,"R6 profile modified")
    old=json.loads(old_raw)
    for k in ("fonts","r3_file_pins","r5_file_pins","parent_commit","parent_file_pins",
              "parent_payload_sha256","parent_manifest_sha256","parent_release_id",
              "modified_parent_files","new_files","new_u2_files","changed_r5_files",
              "source_report_sha256","input_sha256","policy_sha256","r3_file_pins"):
        require(p.get(k)==old.get(k),"R7 lineage drift "+k)
    previous=p.get("r6_file_pins",{})
    require(len(previous)==106 and digest(previous)==R6_PAYLOAD_SHA,"R6 byte pins drift")
    changed=p.get("changed_r6_files",[])
    require(len(changed)==56 and len(set(changed))==56
            and all(x.endswith(".html") and x!="404.html" for x in changed),
            "R7 must change exactly the 56 public HTML files")
    require(len(p.get("r7_html_pins",{}))==56
            and set(p["r7_html_pins"])==set(changed),"R7 HTML pin scope")
    requires={"phuket-universe.html":{"fonts":["Unbounded-ru-en.woff2","Manrope-latin.woff2","Manrope-cyrillic.woff2"],
              "font_bytes":91352,"css_br":10324,"css_br_max":10496,"first_br":19766,
              "first_br_max":19968,"first_gzip":23686,"first_gzip_max":23808,
              "first_with_fonts":111118,"first_with_fonts_max":111360},
              "en/phuket-universe.html":{"fonts":["Unbounded-ru-en.woff2","Manrope-latin.woff2"],
              "font_bytes":76852,"css_br":10324,"css_br_max":10496,"first_br":18950,
              "first_br_max":19200,"first_gzip":22783,"first_gzip_max":23040,
              "first_with_fonts":95802,"first_with_fonts_max":96256}}
    require(p.get("transfer_profiles")==requires,"R7 transfer budgets drift")
    overrides=p.get("source_override_sha256",{})
    require(set(overrides)==set(old["source_override_sha256"]),"R7 historical source scope")
    require(len(p.get("r7_source_sha256",{}))==17,"R7 new source pin count")
    return p

def verify_integrity()->dict:
    p=profile()
    raw=(LIVE/"_release.json").read_bytes()
    require(sha(raw)==MANIFEST_SHA,"R7 manifest SHA drift")
    m=json.loads(raw)
    rows=m.get("files",[])
    require(m.get("schema")=="ai-skill-lab.static-release.v1"
            and m.get("release_id")==RELEASE and m.get("file_count")==107
            and len(rows)==107 and len({x["path"] for x in rows})==107,
            "R7 manifest identity/file list")
    actual={}
    for file in LIVE.rglob("*"):
        require(not file.is_symlink(),"R7 symlink not allowed")
        if file.is_file() and file.name!="_release.json":
            data=file.read_bytes()
            actual[file.relative_to(LIVE).as_posix()]={"size":len(data),"sha256":sha(data)}
    expected={x["path"]:{"size":x["size"],"sha256":x["sha256"]} for x in rows}
    require(actual==expected and digest(actual)==PAYLOAD_SHA and m.get("payload_sha256")==PAYLOAD_SHA,
            "R7 content/manifest mismatch")
    previous=p["r6_file_pins"]
    require(set(actual)-set(previous)==NEW_FILE and not(set(previous)-set(actual))
            and {x for x in previous if actual[x]!=previous[x]}==set(p["changed_r6_files"]),
            "R7 changes exceed 56 public HTML + one script")
    require({x:actual[x] for x in p["r7_html_pins"]}==p["r7_html_pins"],"R7 exact public page pins")
    fonts={k:v for k,v in actual.items() if k.endswith(".woff2")}
    require(fonts==p["fonts"] and sum(x["size"] for x in fonts.values())==121388,"R7 immutable fonts drift")
    require(sum(x["size"] for x in actual.values())==1362928,"R7 byte count drift")
    events=(LIVE/"phuket-universe-events.js").read_bytes()
    require(b"const ENABLED = false;" in events and events==(ROOT/"public/phuket-universe-events.js").read_bytes(),
            "R7 event runtime enabled or differing from reviewed source")
    return {"release":RELEASE,"files":107,"routes":56,"workshop_routes":54,
            "r6_files_unchanged":50,"payload_bytes":1362928,"font_bytes":121388,
            "real_listings":0,"events_enabled":False}

def check_release()->dict:
    result=verify_integrity()
    p=profile()
    from build_phuket_universe_r7 import render
    from phuket_release_profile import universe_page
    observed={x.relative_to(LIVE).as_posix():x.read_bytes() for x in LIVE.rglob("*") if x.is_file()}
    require(render()==observed,"R7 immutable R6 reproduction differs")
    for k in p["r7_source_sha256"]:
        require(sha((ROOT/k).read_bytes())==p["r7_source_sha256"][k],"R7 reviewed source pin drift "+k)
    for k,v in p["source_override_sha256"].items():
        require(sha((ROOT/k).read_bytes())==v,"R7 historical gate source pin drift "+k)
    for page in PAGES:
        require(universe_page(LIVE/page),"R7 Universe shell mismatch")
        text=(LIVE/page).read_text(encoding="utf-8")
        require("id=\"agency-pilot-terms\"" in text and 'data-u2-catalog=""' in text
                and "data-u2-card" not in text and text.count('data-universe-event="project_click"')==5,
                "R7 Universe content integrity")
    for name in ("schema/public_event_daily_e38.sql",
                 "services/lead-ingress/api/event.js","services/lead-receiver-cloudflare/src/index.js",
                 "services/lead-receiver-cloudflare/wrangler.jsonc",
                 "package-lock.json","package.json"):
        old=subprocess.run(["git","-C",str(ROOT),"show",R6_HEAD+":"+name],
             capture_output=True,timeout=30)
        require(old.returncode==0 and old.stdout==(ROOT/name).read_bytes(),
                "R7 prohibited ingress/schema/dependency mutation: "+name)
    return result

def legacy_r6_html(rel: str) -> bytes:
    """Exact inverse for inherited pre-U3 text/SEO gates, NOT an exemption.

    R7 rendered file must first match independently SHA-pinned U3 bytes and the
    transformation of the SHA-pinned R6 Git blob. Historical checks only read
    the recovered immutable R6 content, retaining every previous assertion.
    R7-specific changes are separately covered by check_release and 9 tests.
    """
    p = profile()
    require(rel in p["changed_r6_files"], "legacy normalization outside R7 56-route scope")
    original = subprocess.run(["git", "-C", str(ROOT), "show",
                               R6_HEAD + ":deploy/live/" + rel],
                              capture_output=True, timeout=30)
    require(original.returncode == 0, "R6 immutable page not available")
    old = original.stdout
    pinned = p["r6_file_pins"][rel]
    require(len(old) == pinned["size"] and sha(old) == pinned["sha256"],
            "R6 page hash/size changed")
    current = (LIVE / rel).read_bytes()
    new_pin = p["r7_html_pins"][rel]
    require(len(current) == new_pin["size"] and sha(current) == new_pin["sha256"],
            "R7 page hash/size changed")
    from build_phuket_universe_r7 import make_page
    expected = make_page(rel, old.decode("utf-8")).encode("utf-8")
    require(expected == current, "R7 markup not exactly approved additive transformation")
    return old
