"""Fail-closed SHA-256 successor evidence for the unapproved bilingual /method candidate.

No production mutation, no release authority and no replacement of historical pins.
"""
from __future__ import annotations
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
import hashlib,json,re,subprocess

ROOT=Path(__file__).resolve().parents[1]
BUNDLE=ROOT/"docs/release-candidates/seo-method-r1-20261121"
PARENT_COMMIT="b40470c884715ec580edd0beefb175d50ea0e660"
PARENT_SHA="79ecdcd892a308ef3ae93b6f551a4c01e59e9a584eee39764daba5498df11889"
NEW_MANIFEST_SHA="ef0bc7d77b523c480fa78e3ea4c87ac1ebfbffc2567f461b077b9328c7341ab0"
NEW_PAYLOAD_SHA="f2678f7fb3ff5381e421795f83bd8115fa7365613806443cfeea9802efacdf88"
NEW_ARCHIVE_SHA="189f273538137c2d4603a7bd9f25b8969e1deed5c7314c2e5509092ecd89b56d"
RELEASE_ID="AISL_SEO_METHOD_R1_DRAFT_20261121"
CHANGED=frozenset({"method.html","en/method.html","sitemap.xml"})
SOURCE_SHA={
 "app/(ru)/method/page.tsx":"ada13cf8a2f95e8443b2a55039c36a9732378b4643d68f15115d9ef8a6ba345c",
 "app/(en)/en/method/page.tsx":"67aa5fa4440a398bf43c50829fe8e3693b29b76af81e6d490c82b5289919fc59"
}
class SuccessorDeny(ValueError): pass
def require(ok,reason):
 if not ok: raise SuccessorDeny("SEO_METHOD_RELEASE_DENY:"+reason)
def digest(blob:bytes)->str: return hashlib.sha256(blob).hexdigest()
# Two exact rendered main digests, not derived from a mutable live page.
MAIN_STATIC_SHA={
 "method.html":"288f506d8a2b9c2e21eda2716e988408ab3dd685a4b8b9fdb6e0bdc6b9c3c636",
 "en/method.html":"b789e3ff45dfc8161ecb7b9aa2c634ebc09b6b620587eccd0e2ce9924f9b0cde"
}
def active()->bool:
 try:
  raw=(ROOT/"deploy/live/_release.json").read_bytes()
  if digest(raw)!=NEW_MANIFEST_SHA:return False
  m=json.loads(raw)
  return m.get("release_id")==RELEASE_ID and m.get("patch_id")==RELEASE_ID and m.get("parent_manifest_sha256")==PARENT_SHA
 except (OSError,ValueError,TypeError):return False
def lineage_active():
 from adult_analytics_lineage import current_release
 return active() or current_release().active()

def verified_live_lineage():
 """Run the exact release proof before inheriting unchanged method-generation gates."""
 from adult_analytics_lineage import current_release
 adult = current_release()
 if adult.active():
  adult.verify()
  # The prior review bundle and method sources must still satisfy their original seals.
  verify()
 elif active():
  verify(require_live=True)
 else:
  return False
 return True

def inherited_gate_family(release_id: str) -> str:
 # Only unchanged historical content may use the R7B/SITE-A2 gate family.
 # This is not a release-id alias in the on-disk manifest or production policy.
 from adult_analytics_lineage import certificate_donors, current_release, diagnostic, guide_donors, r3, sitemap_dates, telegram_card, universe_home, restored_guides, matcher_brief
 if release_id in {RELEASE_ID, r3.RELEASE_ID, guide_donors.RELEASE_ID, diagnostic.RELEASE_ID, sitemap_dates.RELEASE_ID, certificate_donors.RELEASE_ID, telegram_card.RELEASE_ID, universe_home.RELEASE_ID, restored_guides.RELEASE_ID, matcher_brief.RELEASE_ID}:
  adult = current_release()
  require(active() if release_id == RELEASE_ID else
          adult.active() and adult.RELEASE_ID == release_id, "RELEASE_PROFILE_UNSEALED")
  require(verified_live_lineage(),"RELEASE_PROFILE_UNSEALED")
  return "PHUKET_UNIVERSE_U3_E38_DORMANT_R7B_20261015"
 return release_id
def trusted_git(*args)->bytes:
 p=subprocess.run(["git","-C",str(ROOT),*args],capture_output=True,timeout=15,check=False)
 require(p.returncode==0,"GIT_HISTORY")
 return p.stdout
def parent_file(rel:str)->bytes:
 return trusted_git("show",PARENT_COMMIT+":deploy/live/"+rel)
def single_main(blob:bytes)->bytes:
 rows=re.findall(rb'<main id="main"[\s\S]*?</main>',blob)
 require(len(rows)==1,"EXACT_MAIN")
 return rows[0]
def verify(*,source_overrides=None,file_overrides=None,archive_override=None,manifest_override=None,require_live=False):
 # Parent must be a confirmed ancestor, not a user-supplied path or revision.
 require(trusted_git("merge-base","--is-ancestor",PARENT_COMMIT,"HEAD")==b"","PARENT_NOT_ANCESTOR")
 old_manifest_bytes=parent_file("_release.json")
 require(digest(old_manifest_bytes)==PARENT_SHA,"PARENT_MANIFEST_SHA")
 old=json.loads(old_manifest_bytes)
 require(old.get("file_count")==108 and len(old.get("files",[]))==108,"PARENT_COUNT")
 old_rows={r["path"]:r for r in old["files"]}
 require(len(old_rows)==108,"PARENT_DUPLICATE")
 manifest=manifest_override if manifest_override is not None else (BUNDLE/"manifest.json").read_bytes()
 require(digest(manifest)==NEW_MANIFEST_SHA,"CANDIDATE_MANIFEST_SHA")
 m=json.loads(manifest)
 require(set(m)=={"schema","release_id","patch_id","file_count","payload_sha256","parent_manifest_sha256","files"},"NEW_MANIFEST_FIELDS")
 require(m["schema"]=="ai-skill-lab.static-release.v1" and m["release_id"]==RELEASE_ID
   and m["patch_id"]==RELEASE_ID and m["parent_manifest_sha256"]==PARENT_SHA
   and m["file_count"]==108,"NEW_MANIFEST_IDENTITY")
 rows=m["files"]
 require(len(rows)==108 and len({r["path"] for r in rows})==108,"NEW_FILE_COUNT")
 bypath={r["path"]:r for r in rows}
 require(set(bypath)==set(old_rows),"NEW_FILESET")
 for p,r in bypath.items():
  require(set(r)=={"path","size","sha256"} and isinstance(r["size"],int)
   and isinstance(r["sha256"],str) and "/" not in p[:1]
   and "\\" not in p and ".." not in Path(p).parts,"ROW_SCHEMA_OR_PATH:"+p)
 aggregate="".join(f"{r['path']}\t{r['size']}\t{r['sha256']}\n" for r in sorted(rows,key=lambda r:r["path"])).encode()
 require(digest(aggregate)==NEW_PAYLOAD_SHA==m["payload_sha256"],"AGGREGATE_SHA")
 changed={p for p,r in bypath.items() if (r["size"],r["sha256"])!=(old_rows[p]["size"],old_rows[p]["sha256"])}
 require(changed==CHANGED,"EXACT_THREE_FILE_DELTA")
 archive=archive_override if archive_override is not None else (BUNDLE/"review.zip").read_bytes()
 require(digest(archive)==NEW_ARCHIVE_SHA,"ARCHIVE_SHA")
 with ZipFile(BytesIO(archive)) as z:
  names=z.namelist()
  require(len(names)==len(set(names))==109 and set(names)==set(bypath)|{"_release.json"},"ARCHIVE_FILESET")
  require(z.read("_release.json")==manifest,"ARCHIVE_MANIFEST")
  files={p:z.read(p) for p in bypath}
 if file_overrides: files.update(file_overrides)
 for p,r in bypath.items():
  require(len(files[p])==r["size"] and digest(files[p])==r["sha256"],"PAYLOAD_BYTE:"+p)
 require(set(files)==set(bypath),"OVERRIDE_FILESET")
 # A reviewed child changes EN source. Verify the historical archive against its
 # pinned pre-edit source and give explicit negative fixtures precedence.
 from adult_analytics_lineage import has_guide_links, guide_donors
 sources = guide_donors.old_method_source() if has_guide_links() else {}
 sources.update(source_overrides or {})
 # Original legal/header/CTA envelopes must be identical on each changed method route.
 for page,source in (("method.html","app/(ru)/method/page.tsx"),("en/method.html","app/(en)/en/method/page.tsx")):
  parent=parent_file(page)
  require(len(parent)==old_rows[page]["size"] and digest(parent)==old_rows[page]["sha256"],"PARENT_PAGE:"+page)
  current=files[page]
  first,second=single_main(parent),single_main(current)
  require(parent.replace(first,b"__MAIN__",1)==current.replace(second,b"__MAIN__",1),"OUTER_SHELL:"+page)
  require(b'method-example' in second and b'<h2 id="method-example">' in second
    and second.count(b"<article")==5 and second.count(b"<h1")==1
    and b"<script" not in second and b"<form" not in second,"PAGE_BOUNDARY:"+page)
  require(current==(BUNDLE/page).read_bytes(),"REVIEW_PAGE_BYTES:"+page)
  raw=sources.get(source)
  if raw is None:raw=(ROOT/source).read_bytes()
  require(digest(raw)==SOURCE_SHA[source],"SOURCE_SHA:"+source)
 # No new, removed or changed sitemap URL; only two known updated lastmod values.
 original=parent_file("sitemap.xml").decode("utf-8")
 for route in ("/method","/en/method"):
  before=f"<loc>https://aiskillab.work{route}</loc><lastmod>2026-10-16</lastmod>"
  after=f"<loc>https://aiskillab.work{route}</loc><lastmod>2026-11-21</lastmod>"
  require(original.count(before)==1,"OLD_SITEMAP_ROW:"+route)
  original=original.replace(before,after,1)
 require(files["sitemap.xml"]==original.encode("utf-8")
   ==(BUNDLE/"sitemap.xml").read_bytes(),"ONLY_TWO_SITEMAP_LASTMODS")
 html_routes={p for p in bypath if p.endswith(".html") and p!="404.html"}
 require(len(html_routes)==56,"EXACT_56_PUBLIC_ROUTES")
 if require_live:
  live=ROOT/"deploy/live"
  present={p.relative_to(live).as_posix() for p in live.rglob("*") if p.is_file()}
  require(present==set(bypath)|{"_release.json"},"LIVE_FILESET")
  require((live/"_release.json").read_bytes()==manifest,"LIVE_MANIFEST")
  for p,r in bypath.items():
   require((live/p).read_bytes()==files[p],"LIVE_BYTE:"+p)
 return {"status":"CANDIDATE_VALIDATED_NOT_ADMITTED" if not require_live else "STATIC_PAYLOAD_MATCH_ONLY",
         "release_id":RELEASE_ID,"file_count":108,"public_routes":56,
         "changed":sorted(CHANGED),"parent_manifest_sha256":PARENT_SHA,
         "manifest_sha256":NEW_MANIFEST_SHA,"production_authority":False}
if __name__=="__main__":
 print("SEO_METHOD_RELEASE_EVIDENCE_PASS "+json.dumps(verify(),sort_keys=True))
