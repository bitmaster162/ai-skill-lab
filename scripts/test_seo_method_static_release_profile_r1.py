"""Negative and inheritance fixtures for unapproved /method static successor."""
from adult_analytics_lineage import current_release, diagnostic, guide_donors, r3
adult = current_release()
from seo_method_static_release_profile_r1 import verify,SuccessorDeny,ROOT,BUNDLE,RELEASE_ID,active,inherited_gate_family
result=verify()
assert result["status"]=="CANDIDATE_VALIDATED_NOT_ADMITTED"
assert result["release_id"]==RELEASE_ID and result["public_routes"]==56
assert result["production_authority"] is False
assert result["changed"]==["en/method.html","method.html","sitemap.xml"]
denied=0
def reject(note,prefix,**kwargs):
 global denied
 try: verify(**kwargs)
 except SuccessorDeny as error:
  assert str(error).startswith("SEO_METHOD_RELEASE_DENY:"+prefix),note+":"+str(error)
  denied+=1
 else: raise AssertionError("FAIL_OPEN:"+note)
src=ROOT/"app/(ru)/method/page.tsx"
source=src.read_bytes()
assert b"method-example" in source
reject("source_sha","SOURCE_SHA",source_overrides={"app/(ru)/method/page.tsx":source.replace(b"method-example",b"method-changed",1)})
ru=(BUNDLE/"method.html").read_bytes()
reject("modified_html","PAYLOAD_BYTE",file_overrides={"method.html":ru+b" "})
reject("missing_html","PAYLOAD_BYTE",file_overrides={"en/method.html":b""})
reject("unapproved_asset","OVERRIDE_FILESET",file_overrides={"malicious.html":b"<script></script>"})
manifest=(BUNDLE/"manifest.json").read_bytes()
reject("manifest_drift","CANDIDATE_MANIFEST_SHA",manifest_override=manifest+b" ")
archive=(BUNDLE/"review.zip").read_bytes()
reject("archive_mutation","ARCHIVE_SHA",archive_override=archive[:-1]+bytes([archive[-1]^1]))
reject("archive_truncated","ARCHIVE_SHA",archive_override=archive[:-1])
if active():
 evidence=verify(require_live=True)
 assert evidence["status"]=="STATIC_PAYLOAD_MATCH_ONLY"
 reject("live_mutated_html","PAYLOAD_BYTE",require_live=True,file_overrides={"method.html":ru+b" "})
elif adult.active():
 reject("successor_has_distinct_inventory","LIVE_FILESET",require_live=True)
 if guide_donors.active() or diagnostic.active():
  # The child source is valid for its own release but cannot stand in for archived R1.
  en = "app/(en)/en/method/page.tsx"
  reject("child_source_in_old_release", "SOURCE_SHA", source_overrides={en: (ROOT/en).read_bytes()})
  try:
   inherited_gate_family(r3.RELEASE_ID)
  except SuccessorDeny as error:
   assert "RELEASE_PROFILE_UNSEALED" in str(error)
   denied += 1
  else:
   raise AssertionError("ancestor release ID accepted for a different active child")
else:
 reject("old_release_not_live_candidate","LIVE_MANIFEST",require_live=True)
print(f"SEO_METHOD_STATIC_SUCCESSOR=PASS candidate_files=108 immutable_parent=PASS changed=3 public_routes=56 negative_fixtures={denied} release_authority=DENY")
