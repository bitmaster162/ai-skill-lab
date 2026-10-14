#!/usr/bin/env python3
"""Acceptance for the two-paragraph R2 edit; no release or external API calls."""
from __future__ import annotations

import argparse
import json
import sys
import unittest
from unittest.mock import patch

import prepare_phuket_universe_static_r2 as candidate
import test_phuket_universe_static_r1 as inherited


class StaticU1TermsR2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files, cls.stats = candidate.render()
        cls.r1 = candidate.sealed_r1()

    def test_only_two_paragraphs_and_new_manifest_change(self):
        self.assertEqual(set(self.files), set(self.r1))
        changed = {n for n in self.files if self.files[n] != self.r1[n]}
        self.assertEqual(changed, {"phuket-universe.html", "en/phuket-universe.html", "_release.json"})
        for locale, route in candidate.ROUTES.items():
            name = route.lstrip("/") + ".html"
            expected = self.r1[name].decode("utf-8").replace(candidate.REMOVED_PARAGRAPHS[locale], "", 1)
            self.assertEqual(self.files[name], expected.encode("utf-8"))

    def test_terms_removed_contacts_and_structure_kept(self):
        for locale, route in candidate.ROUTES.items():
            text = self.files[route.lstrip("/") + ".html"].decode("utf-8")
            self.assertNotIn("[УСЛОВИЯ ДЛЯ АГЕНТСТВ]", text)
            self.assertNotIn("[TERMS FOR AGENCIES]", text)
            self.assertIn('id="agencies"', text)
            self.assertIn("mailto:robert@aiskillab.work", text)
            self.assertEqual(text.count('<svg '), 8)

    def test_missing_or_duplicate_paragraph_rejected(self):
        for locale, exact in candidate.REMOVED_PARAGRAPHS.items():
            for bad in ("", exact + exact, exact.replace("pu-s100", "other-class")):
                with self.subTest(locale=locale), self.assertRaisesRegex(RuntimeError, "missing or duplicated"):
                    candidate.remove_terms_paragraph(bad, locale)

    def test_deterministic_new_manifest_and_r1_unchanged(self):
        again, stats = candidate.render()
        self.assertEqual(again, self.files)
        self.assertEqual(stats, self.stats)
        self.assertEqual(candidate.sealed_r1(), self.r1)
        payload = {n: b for n, b in self.files.items() if n != "_release.json"}
        m = candidate.previous.verify_manifest(payload, self.files["_release.json"])
        self.assertEqual(m["release_id"], candidate.RELEASE)
        self.assertEqual(m["file_count"], 104)
        self.assertEqual(self.stats["r1_payload_files_unchanged"], 102)

    def test_no_new_terms_or_release_authority(self):
        for flag in ("release_authorized", "deploy_authorized", "production_ready", "public_agency_terms_published"):
            self.assertIs(self.stats[flag], False)
        self.assertEqual(self.stats["agency_terms_status"], "NOT_DEFINED_RESEARCH_REQUIRED")
        self.assertEqual(self.files["vercel.json"], self.r1["vercel.json"])
        self.assertEqual(self.files["lab-command.js"], self.r1["lab-command.js"])
        self.assertTrue(self.stats["publication_holds"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", action="store_true")
    args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(StaticU1TermsR2Tests))
    if not result.wasSuccessful():
        raise SystemExit(1)
    if args.browser:
        with patch.object(inherited, "candidate", candidate):
            cases = inherited.browser_acceptance(screenshots=False)
        print("R2_BROWSER_PASS", len(cases), "real_api_requests=0", flush=True)
    print("R2_TWO_PARAGRAPHS_REMOVED_PUBLICATION_HOLD", flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
