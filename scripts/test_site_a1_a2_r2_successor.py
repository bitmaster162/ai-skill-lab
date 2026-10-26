#!/usr/bin/env python3
"""Negative fail-closed successor and immutable historical R7B regression."""
from __future__ import annotations
import io,hashlib,json,subprocess,tarfile,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import site_a1_a2_r2_successor as s
import phuket_universe_r7b_release_profile as r7b

class ExactSuccessorTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.current=(s.LIVE/"_release.json").read_bytes()
  cls.old=s.git_blob(s.CHAIN[0][0],"deploy/live/_release.json")
 def test_r2_exact_admission(self):
  proof=s.verify()
  self.assertEqual(proof["static_assets"],108)
  self.assertEqual(proof["r7b_immutable_ancestors"],6)
  self.assertFalse(proof["production_authority"])
 def test_unknown_patch_rejected(self):
  changed=json.loads(self.current)
  changed["patch_id"]="UNAPPROVED"
  with self.assertRaisesRegex(s.SuccessorHold,"SUCCESSOR_MANIFEST_SHA"):
   s.verify(manifest_override=json.dumps(changed).encode())
 def test_other_sha_rejected(self):
  corrupt=self.current.replace(b'SITE_A1_A2_R2_20261026_DRAFT_REVIEW',
                               b'SITE_A1_A2_R2_20261026_DRAFT_REVIEw')
  self.assertNotEqual(corrupt,self.current)
  with self.assertRaisesRegex(s.SuccessorHold,"SUCCESSOR_MANIFEST_SHA"):
   s.verify(manifest_override=corrupt)
 def test_extra_static_file_rejected(self):
  with self.assertRaisesRegex(s.SuccessorHold,"ACTUAL_ASSET_MISMATCH"):
   s.verify(extra_file="unapproved.html")
 def test_ancestor_missing_rejected(self):
  with self.assertRaisesRegex(s.SuccessorHold,"CHAIN_MISSING_ANCESTOR"):
   s.verify(drop_ancestor=s.CHAIN[2][0])
 def test_historical_manifest_tamper_rejected(self):
  old=self.old.replace(b'PHUKET_UNIVERSE_U3_E38_DORMANT_R7B_20261015',
                      b'PHUKET_UNIVERSE_U3_E38_DORMANT_R7B_20261014')
  self.assertNotEqual(old,self.old)
  with self.assertRaisesRegex(s.SuccessorHold,"HISTORIC_MANIFEST_SHA"):
   s.verify(historical_override=old)
 def test_historic_r7b_rules_exact_byte_identity(self):
  for file in s.HISTORIC_FILES:
   self.assertEqual(s.git_blob("HEAD",file),s.git_blob(s.BASE,file),file)
  self.assertEqual(s.sha(self.old),s.CHAIN[0][1])
 def test_historical_r7b_gate_on_its_original_payload(self):
  # A temporary fixture reproduces R7B from exact Git history; never patch old
  # checker rules. Only module path/immutable Git retrieval is fixture-bound.
  data=subprocess.run(["git","--no-optional-locks","-C",str(s.ROOT),
                       "archive","--format=tar",s.CHAIN[0][0],"deploy/live"],
                      check=True,capture_output=True,timeout=45).stdout
  with tempfile.TemporaryDirectory(prefix="site_a2_r7b_historical_") as td:
   root=Path(td);live=root/"deploy/live";live.mkdir(parents=True,exist_ok=True)
   with tarfile.open(fileobj=io.BytesIO(data),mode="r:") as archive:
    for item in archive:
     name=Path(item.name)
     if item.isdir():continue
     self.assertFalse(item.issym() or item.islnk())
     self.assertEqual(name.parts[:2],("deploy","live"))
     dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True)
     f=archive.extractfile(item)
     self.assertIsNotNone(f)
     dest.write_bytes(f.read())
   wf=root/r7b.CI_WORKFLOW
   wf.parent.mkdir(parents=True,exist_ok=True)
   wf.write_bytes(s.git_blob(s.BASE,r7b.CI_WORKFLOW))
   with patch.object(r7b,"ROOT",root),patch.object(r7b,"LIVE",live),patch.object(r7b,"git_blob",s.git_blob):
    status=r7b.verify_integrity() # original R7B code and SHA pins
   self.assertEqual(status["files"],107)
   self.assertEqual(status["release"],r7b.RELEASE)
   self.assertEqual(status["routes"],56)
if __name__=="__main__":
 unittest.main(verbosity=2)
