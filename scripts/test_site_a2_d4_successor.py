"""Fail-closed tests for exact R2 Workshop D4 successor only."""
import json
import unittest
from pathlib import Path
from site_a2_d4_successor import (
    verify_identity, verify_sitemap, semantic, exact_payload_limit,
    EXACT_PAYLOAD, MANIFEST_SHA, ADMISSION_SHA, PINNED,
)
ROOT = Path(__file__).resolve().parents[1]
M = (ROOT/"deploy/live/_release.json").read_bytes()
A = (ROOT/"data/SITE_A1_A2_R2_METADATA_SUCCESSOR_ADMISSION_V2_20261026.json").read_bytes()

class ExactD4Test(unittest.TestCase):
    def test_exact_successor(self):
        self.assertTrue(verify_identity(M, A, EXACT_PAYLOAD))
        self.assertTrue(verify_sitemap(ROOT))
        self.assertEqual(len(PINNED),6)
    def test_wrong_manifest_fail(self):
        with self.assertRaisesRegex(ValueError,"SHA"):
            verify_identity(M+b" ", A, EXACT_PAYLOAD)
    def test_wrong_admission_fail(self):
        with self.assertRaisesRegex(ValueError,"SHA"):
            verify_identity(M, A+b" ", EXACT_PAYLOAD)
    def test_extra_byte_fail(self):
        with self.assertRaisesRegex(ValueError,"payload"):
            verify_identity(M, A, EXACT_PAYLOAD+1)
    def test_missing_byte_fail(self):
        with self.assertRaisesRegex(ValueError,"payload"):
            exact_payload_limit(EXACT_PAYLOAD-1)
    def test_unknown_patch_fail(self):
        wrong=json.loads(M)
        wrong["patch_id"]="INVALID_RELEASE"
        with self.assertRaisesRegex(ValueError,"SHA"):
            verify_identity(json.dumps(wrong).encode(), A, EXACT_PAYLOAD)
    def test_english_ru_tokens_preserved(self):
        self.assertEqual(semantic("studio.html","CUSTOM SCOPE","CUSTOM SCOPE"),"ИНДИВИДУАЛЬНЫЙ ОБЪЁМ")
        self.assertEqual(semantic("en/studio.html","CUSTOM SCOPE","CUSTOM SCOPE"),"CUSTOM SCOPE")
        self.assertEqual(semantic("challenge.html","DEFINE","DEFINE"),"ЦЕЛЬ")
if __name__ == "__main__":
    unittest.main(verbosity=2)
