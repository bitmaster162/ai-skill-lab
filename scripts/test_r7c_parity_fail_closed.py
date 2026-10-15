#!/usr/bin/env python3
"""Offline R7C lineage and negative-tamper tests, without disk mutation."""
from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch
import phuket_terms_withdrawal_r7c_profile as gate


class R7CParityRegression(unittest.TestCase):
    def test_exact_scoped_release(self):
        result = gate.check_release()
        self.assertEqual(result["status"], "LOCAL_PASS")
        self.assertEqual(result["manifest_sha256"], gate.R7C_MANIFEST_SHA)
        self.assertEqual(set(result["changed_html"]), set(gate.NOTES))
        self.assertFalse(result["universe_events_enabled"])
        self.assertFalse(result["production_authority"])

    def test_pinned_lineage_of_withdrawn_pages(self):
        gate.check_release()
        for rel in gate.NOTES:
            old = gate.legacy_r6_html_for_parity(rel)
            self.assertTrue(old.startswith(b"<!doctype html>"))
            self.assertNotIn(b'agency-listing-terms', old)

    def test_manifest_byte_drift_denied(self):
        manifest = gate.LIVE / "_release.json"
        original = Path.read_bytes

        def changed(path):
            value = original(path)
            return value + b" " if path == manifest else value

        with patch.object(Path, "read_bytes", changed):
            with self.assertRaisesRegex(ValueError, "r7c_manifest_sha_drift"):
                gate.check_release()

    def test_one_character_of_public_note_denied(self):
        page = gate.LIVE / "phuket-universe.html"
        original = Path.read_bytes
        encoded = gate.NOTES["phuket-universe.html"].encode("utf-8")

        def changed(path):
            value = original(path)
            if path == page:
                if value.count(encoded) != 1:
                    raise AssertionError("original RU exact note missing")
                return value.replace(encoded, b"unauthorized-text", 1)
            return value

        with patch.object(Path, "read_bytes", changed):
            with self.assertRaisesRegex(ValueError, "manifest_asset_mismatch"):
                gate.check_release()

    def test_source_copy_drift_denied(self):
        source = gate.ROOT / "components/phuketUniverseAgencyTerms.ts"
        original = Path.read_text

        def changed(path, *args, **kwargs):
            contents = original(path, *args, **kwargs)
            return contents.replace("Listing terms are discussed individually", "unapproved terms", 1) if path == source else contents

        with patch.object(Path, "read_text", changed):
            with self.assertRaisesRegex(ValueError, "source_copy_parity"):
                gate.check_release()


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(R7CParityRegression)
    )
    if not result.wasSuccessful():
        raise SystemExit(1)
    print("R7C_PARITY_FAIL_CLOSED_PASS tests=5 legacy_provenance=true disk_writes=0")
