#!/usr/bin/env python3
"""Offline-only R7B freshness correction checks; R7 HEAD remains immutable."""
from __future__ import annotations
import hashlib,json,unittest
from pathlib import Path
from unittest.mock import patch
import phuket_universe_r7b_release_profile as profile
from build_phuket_universe_r7b import r7_parent,render

class R7BFreshnessTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r7=r7_parent()
  cls.r7b={p.relative_to(profile.LIVE).as_posix():p.read_bytes()
           for p in profile.LIVE.rglob("*") if p.is_file()}
 def test_only_sitemap_and_manifest_mutate(self):
  self.assertEqual(len(self.r7),len(self.r7b))
  self.assertEqual({k for k in self.r7 if self.r7[k]!=self.r7b[k]},
                   {"sitemap.xml","_release.json"})
  self.assertEqual(render(),self.r7b)
  result=profile.verify_integrity()
  self.assertEqual((result["files"],result["r7_payload_unchanged"],result["routes"]),(107,106,56))
 def test_source_and_sitemap_lastmod_exact(self):
  text=(profile.LIVE/"sitemap.xml").read_text("utf-8")
  self.assertEqual(text.count("<lastmod>2026-10-15</lastmod>"),56)
  self.assertEqual(text.count("<loc>https://aiskillab.work"),56)
  source=(profile.ROOT/"app/sitemap.ts").read_text("utf-8")
  self.assertEqual(source.count('const lastModified = "2026-10-15";'),1)
  self.assertEqual(source.count('lastModified: universeRoutes.includes(route) ? "2026-10-15" : lastModified'),1)
 def test_parent_sources_remain_byte_frozen(self):
  self.assertEqual(hashlib.sha256(profile.git_blob(profile.PREV_HEAD,
        "data/phuket_universe_u3_e38_r7_profile.json")).hexdigest(),
        profile.PREV_PROFILE_SHA)
  for path in ("app/(ru)/phuket/page.tsx","app/(en)/en/phuket/page.tsx",
               "components/PhuketUniverseTeaser.tsx","components/UniverseFooterLink.tsx",
               "schema/public_event_daily_e38.sql","services/lead-ingress/api/event.js",
               "services/lead-receiver-cloudflare/src/index.js"):
   self.assertEqual((profile.ROOT/path).read_bytes(),profile.git_blob(profile.PREV_HEAD,path))
 def test_r7b_preview_still_empty_and_disabled(self):
  self.assertEqual(self.r7b["phuket-housing-u2.js"],self.r7["phuket-housing-u2.js"])
  self.assertEqual(self.r7b["phuket-universe-events.js"],self.r7["phuket-universe-events.js"])
  self.assertIn(b"const ENABLED = false",self.r7b["phuket-universe-events.js"])
  self.assertTrue(all(b"data-u2-card" not in self.r7b[p] for p in
      ("phuket-universe.html","en/phuket-universe.html")))
  self.assertFalse(any(profile.profile()["authority"].values()))
 def test_manifest_tamper_denied(self):
  original=Path.read_bytes
  manifest=json.loads(self.r7b["_release.json"])
  manifest["files"].append(manifest["files"][0])
  target=profile.LIVE/"_release.json"
  def altered(path):
   return json.dumps(manifest).encode() if path==target else original(path)
  with patch.object(Path,"read_bytes",altered),self.assertRaises(ValueError):
   profile.verify_integrity()
 def test_sitemap_tamper_denied(self):
  original=Path.read_bytes;target=profile.LIVE/"sitemap.xml"
  def altered(path):
   return original(path)+b"unexpected" if path==target else original(path)
  with patch.object(Path,"read_bytes",altered),self.assertRaises(ValueError):
   profile.verify_integrity()
 def test_profile_authority_tamper_denied(self):
  original=Path.read_bytes;target=profile.PROFILE_PATH
  m=json.loads(original(target));m["authority"]["deploy"]=True
  def altered(path):
   return json.dumps(m).encode() if path==target else original(path)
  with patch.object(Path,"read_bytes",altered),self.assertRaises(ValueError):
   profile.profile()
 def test_reviewer_inherited_history_complete(self):
  p=profile.profile()
  self.assertEqual(p["changed_r7_files"],["sitemap.xml"])
  self.assertEqual(len(p["r7_file_pins"]),107)
  self.assertEqual(len(p["r7_html_pins"]),56)
  self.assertEqual(set(p["u3_universe_events"]),
                   {"universe_click","project_click","listing_click"})
  self.assertEqual(p["status"],"RC_LOCAL_ONLY")

def run_units():
 result=unittest.TextTestRunner(verbosity=1).run(
  unittest.defaultTestLoader.loadTestsFromTestCase(R7BFreshnessTests))
 if not result.wasSuccessful():raise ValueError("R7B targeted acceptance failed")
if __name__=="__main__":
 run_units()
 print("PHUKET_R7B_TARGETED_PASS")
