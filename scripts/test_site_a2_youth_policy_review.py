#!/usr/bin/env python3
"""Exact 2026-10-29 factual policy evidence admission; date only, fail closed."""
import json, hashlib, re, subprocess, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/"data/SITE_A2_YOUTH_POLICY_REVIEW_20261029.json"
def sha(b):return hashlib.sha256(b).hexdigest()
class YouthRecheck(unittest.TestCase):
 def test_source_evidence(self):
  evidence=json.loads(E.read_bytes())
  self.assertEqual(evidence["review_date"],"2026-10-29")
  self.assertEqual(len(evidence["sources"]),2)
  urls={r["url"] for r in evidence["sources"]}
  self.assertIn("https://help.openai.com/en/articles/8313401",urls)
  self.assertIn("https://help.openai.com/en/articles/12315553-managing-parental-controls-in-chatgpt",urls)
  for rel,row in evidence["surfaces"].items():
   current=(ROOT/rel).read_bytes()
   self.assertEqual(sha(current),row["sha256_after"])
   self.assertIn(b'data-policy-verified="2026-10-29"',current)
   self.assertNotIn(b'data-policy-verified="2026-09-26"',current)
   old=subprocess.run(["git","-C",str(ROOT),"show","bb2fa49cb1d039aed04d9f89f80af3bccbace7f7:"+rel],
     capture_output=True,check=True).stdout
   self.assertEqual(sha(old),row["sha256_before"])
   old_text=old.decode()
   now_text=current.decode()
   old_date="26 сентября 2026" if row["language"]=="ru" else "September 26, 2026"
   new_date="29 октября 2026" if row["language"]=="ru" else "October 29, 2026"
   restored=now_text.replace('data-policy-verified="2026-10-29"','data-policy-verified="2026-09-26"').replace(new_date,old_date)
   self.assertEqual(restored,old_text)
 def test_review_evidence_pin(self):
  admission=json.loads((ROOT/"data/SITE_A1_A2_R2_METADATA_SUCCESSOR_ADMISSION_V2_20261026.json").read_bytes())
  self.assertEqual(admission["policy_evidence_sha256"],sha(E.read_bytes()))
  self.assertFalse(admission["can_merge"])
  self.assertFalse(admission["can_deploy"])
 def test_tampered_review_denied(self):
  admission=json.loads((ROOT/"data/SITE_A1_A2_R2_METADATA_SUCCESSOR_ADMISSION_V2_20261026.json").read_bytes())
  tampered=E.read_bytes()+b" "
  self.assertNotEqual(admission["policy_evidence_sha256"],sha(tampered))
 def test_youth_gate_immutable(self):
  current=(ROOT/"scripts/check_youth_policy_freshness.py").read_bytes()
  old=subprocess.run(["git","-C",str(ROOT),"show","bb2fa49cb1d039aed04d9f89f80af3bccbace7f7:scripts/check_youth_policy_freshness.py"],capture_output=True,check=True).stdout
  self.assertEqual(current.replace(b"\r\n",b"\n"),old)
if __name__=="__main__": unittest.main(verbosity=2)
