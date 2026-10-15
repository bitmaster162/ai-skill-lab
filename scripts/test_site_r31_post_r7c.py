#!/usr/bin/env python3
"""Strict offline negative gates for owner-reviewed post-R7C form/SEO candidate."""
from __future__ import annotations
import json
from pathlib import Path
import unittest

import build_site_r31_post_r7c as builder
import site_r31_post_r7c_profile as profile


class R31PostR7CTests(unittest.TestCase):
    def test_positive_immutable_candidate(self):
        result = profile.check_release()
        self.assertEqual(result["status"], "LOCAL_PASS")
        self.assertEqual(result["assets"], 108)
        self.assertEqual(result["routes"], 56)
        self.assertEqual(result["manifest_sha256"], builder.EXPECTED_MANIFEST_SHA)
        self.assertFalse(result["production_authority"])

    def test_parent_r7c_lineage_is_exact(self):
        parent, manifest = builder.parent_files()
        current, meta = builder.render()
        self.assertEqual(manifest["file_count"], 107)
        self.assertEqual(builder.sha(builder.git("show", builder.BASE + ":deploy/live/_release.json")),
                         builder.PARENT_MANIFEST_SHA)
        self.assertEqual({k for k in parent if parent[k] != current[k]}, builder.ALLOWED_MODIFIED)
        self.assertEqual(set(current) - set(parent), {"lead-form-runtime.js", "_release.json"})
        for filename in ("phuket-universe.html", "en/phuket-universe.html",
                         "phuket-universe-events.js", "sitemap.xml"):
            self.assertEqual(parent[filename], current[filename], filename)

    def test_source_exactly_reviewed_sha(self):
        builder.verify_git()
        source = builder.git("show", builder.SOURCE + ":public/lead-form-runtime.js")
        self.assertEqual((builder.ROOT / "public/lead-form-runtime.js").read_bytes(), source)

    def test_form_ready_is_fail_closed_without_js(self):
        for locale, rel in (("ru", "start.html"), ("en", "en/start.html")):
            html = (builder.LIVE / rel).read_text("utf-8")
            self.assertEqual(html.count('data-lead-state="unready"'), 1)
            self.assertEqual(html.count('data-lead-readiness'), 1)
            self.assertEqual(html.count('type="submit" disabled'), 1)
            self.assertEqual(html.count('data-lead-direct-contact'), 1)
            self.assertEqual(html.count('/lead-form-runtime.js'), 1)
            self.assertIn(builder.NOTE[locale][0], html)
            self.assertIn(builder.NOTE[locale][1], html)
            self.assertIn('href="#contact-channels"', html)
        react=(builder.ROOT/"components/LeadForm.tsx").read_text("utf-8")
        self.assertIn("useSyncExternalStore", react)
        self.assertIn('disabled={!ready || state === "sending"}', react)

    def test_metadata_exact_three(self):
        generated, _ = builder.render()
        parent, _ = builder.parent_files()
        for source, rel, before, after in builder.SEO:
            new = generated[rel].decode("utf-8")
            old = parent[rel].decode("utf-8")
            self.assertGreaterEqual(old.count(before), 3)
            self.assertEqual(new.count(before), 0)
            self.assertEqual(new.count(after), old.count(before) + old.count(after))
            self.assertEqual((builder.ROOT / source).read_text("utf-8").count(after) >= 1, True)

    def test_manifest_tamper_denied(self):
        raw = (builder.LIVE / "_release.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "byte_mismatch"):
            profile.check_release({"_release.json": raw + b" "})

    def test_r7c_phuket_copy_tamper_denied(self):
        ru = (builder.LIVE / "phuket-universe.html").read_bytes()
        with self.assertRaisesRegex(ValueError, "byte_mismatch"):
            profile.check_release({"phuket-universe.html": ru.replace(
                "Условия размещения".encode(), "Подменено размещение".encode(), 1)})

    def test_one_locale_fail_closed_tamper_denied(self):
        ru = (builder.LIVE / "start.html").read_bytes()
        with self.assertRaisesRegex(ValueError, "byte_mismatch"):
            profile.check_release({"start.html": ru.replace(b'type="submit" disabled',
                                                            b'type="submit"', 1)})

    def test_new_unreviewed_asset_denied(self):
        with self.assertRaisesRegex(ValueError, "inventory_mismatch"):
            profile.check_release({"injected.js": b"unsafe"})

    def test_unreviewed_patch_identity_denied(self):
        raw = (builder.LIVE / "_release.json").read_bytes()
        m = json.loads(raw)
        m["patch_id"] = "UNREVIEWED"
        with self.assertRaisesRegex(ValueError, "byte_mismatch"):
            profile.check_release({"_release.json": json.dumps(m).encode()})

    def test_e38_events_still_dormant(self):
        script = (builder.LIVE / "phuket-universe-events.js").read_bytes()
        self.assertIn(b"const ENABLED = false;", script)
        self.assertNotIn(b"const ENABLED = true;", script)


def run_units():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(R31PostR7CTests)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():
        raise ValueError("R31_POST_R7C_UNITS_FAIL")
    print("R31_POST_R7C_UNITS_PASS cases=11 network_calls=0 production_authority=false")


if __name__ == "__main__":
    run_units()
