#!/usr/bin/env python3
"""Exact SITE-A1/A2 parity admission negative tests. No network or mutation."""
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import check_text_parity as parity

MANIFEST = (ROOT / "deploy/live/_release.json").read_bytes()
ADMISSION = (ROOT / "data/SITE_A1_A2_R2_METADATA_SUCCESSOR_ADMISSION_V2_20261026.json").read_bytes()


class SiteA2ParityAdmission(unittest.TestCase):
    def test_exact_pinned_pair(self):
        parity.require_site_a2_exact_bytes(MANIFEST, ADMISSION)

    def test_wrong_manifest_hash_denied(self):
        damaged = bytearray(MANIFEST)
        damaged[20] ^= 1
        with self.assertRaisesRegex(ValueError, "manifest SHA mismatch"):
            parity.require_site_a2_exact_bytes(bytes(damaged), ADMISSION)

    def test_wrong_admission_hash_denied(self):
        damaged = bytearray(ADMISSION)
        damaged[20] ^= 1
        with self.assertRaisesRegex(ValueError, "admission SHA mismatch"):
            parity.require_site_a2_exact_bytes(MANIFEST, bytes(damaged))

    def test_unknown_patch_denied(self):
        bad = dict(json.loads(MANIFEST))
        bad["patch_id"] = "UNAUTHORIZED_PATCH"
        with self.assertRaisesRegex(ValueError, "manifest SHA mismatch"):
            parity.require_site_a2_exact_bytes(json.dumps(bad).encode(), ADMISSION)


if __name__ == "__main__":
    unittest.main(verbosity=2)
