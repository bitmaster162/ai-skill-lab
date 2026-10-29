"""Fail-closed exact performance successor tests."""
import json
import unittest
from pathlib import Path
from site_a2_exact_performance import approved, EXACT_NON_FONT_BYTES
ROOT = Path(__file__).resolve().parents[1]
M = (ROOT/"deploy/live/_release.json").read_bytes()
A = (ROOT/"data/SITE_A1_A2_R2_METADATA_SUCCESSOR_ADMISSION_V2_20261026.json").read_bytes()

class ExactBudgetTest(unittest.TestCase):
    def test_pinned_successor(self):
        self.assertEqual(approved(M,A,EXACT_NON_FONT_BYTES),EXACT_NON_FONT_BYTES)
    def test_wrong_manifest_denied(self):
        with self.assertRaisesRegex(ValueError,"manifest_SHA"):
            approved(M+b" ",A,EXACT_NON_FONT_BYTES)
    def test_wrong_admission_denied(self):
        with self.assertRaisesRegex(ValueError,"admission_SHA"):
            approved(M,A+b" ",EXACT_NON_FONT_BYTES)
    def test_extra_byte_denied(self):
        with self.assertRaisesRegex(ValueError,"measured_nonfont"):
            approved(M,A,EXACT_NON_FONT_BYTES+1)
    def test_missing_byte_denied(self):
        with self.assertRaisesRegex(ValueError,"measured_nonfont"):
            approved(M,A,EXACT_NON_FONT_BYTES-1)
    def test_wrong_patch_denied(self):
        bad=json.loads(M)
        bad["patch_id"]="NOT_APPROVED"
        with self.assertRaisesRegex(ValueError,"manifest_SHA"):
            approved(json.dumps(bad).encode(),A,EXACT_NON_FONT_BYTES)
if __name__=="__main__":
    unittest.main(verbosity=2)
