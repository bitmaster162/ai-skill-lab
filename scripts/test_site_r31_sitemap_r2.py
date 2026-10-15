#!/usr/bin/env python3
"""Offline negative proof for exact R3.1/R7C sitemap 2026-10-16 successor."""
from __future__ import annotations
import json
from pathlib import Path
import unittest

import build_site_r31_sitemap_r2 as builder
import site_r31_sitemap_r2_profile as profile


class SitemapR2Tests(unittest.TestCase):
    def test_positive_immutable_release(self):
        result = profile.check_release()
        self.assertEqual(result["status"], "LOCAL_PASS")
        self.assertEqual((result["normal_routes"], result["universe_routes"]), (54, 2))
        self.assertEqual(result["assets"], 108)
        self.assertFalse(result["production_authority"])
        self.assertFalse(result["universe_events_enabled"])

    def test_full_parent_and_grandparent_chain(self):
        files, previous = builder.parent_files()
        self.assertEqual(builder.sha(files["_release.json"]), builder.PARENT_MANIFEST_SHA)
        self.assertEqual(previous["parent_manifest_sha256"], builder.GRANDPARENT_MANIFEST_SHA)
        self.assertEqual(previous["file_count"], 108)
        expected, new = builder.render()
        self.assertEqual(new["manifest_sha256"], builder.EXPECTED_MANIFEST_SHA)
        self.assertEqual(new["payload_sha256"], builder.EXPECTED_PAYLOAD_SHA)
        self.assertEqual(expected["_release.json"], (builder.LIVE / "_release.json").read_bytes())

    def test_sitemap_only_asset_change(self):
        old, _ = builder.parent_files()
        new, _ = builder.render()
        changed = {p for p in old if old[p] != new[p]}
        self.assertEqual(changed, {"sitemap.xml", "_release.json"})
        self.assertEqual(set(old), set(new))
        self.assertEqual(len(old), 109)
        for rel in ("start.html", "en/start.html", "lead-form-runtime.js",
                    "phuket-universe-events.js", "phuket-universe.html",
                    "en/phuket-universe.html", "en.html", "en/guides/ai-safety-for-kids.html"):
            self.assertEqual(old[rel], new[rel], rel)

    def test_date_cardinality_and_universe_special_fields(self):
        sitemap = (builder.LIVE / "sitemap.xml").read_text("utf-8")
        rows = builder.XML_ROW.findall(sitemap)
        self.assertEqual(len(rows), 56)
        self.assertEqual(len(set(path for path, _ in rows)), 56)
        self.assertEqual(sum(date == builder.NORMAL_DAY for _, date in rows), 54)
        self.assertEqual(sum(date == builder.UNIVERSE_DAY for _, date in rows), 2)
        self.assertEqual({p for p, v in rows if v == builder.UNIVERSE_DAY}, builder.UNIVERSE_PATHS)
        self.assertEqual(sitemap.count('<changefreq>monthly</changefreq><priority>0.8</priority>'), 2)

    def test_only_one_source_lastmod_changes(self):
        builder.verify_source()
        baseline = builder.git("show", builder.BASE + ":app/sitemap.ts").replace(b"\r\n", b"\n")
        observed = (builder.ROOT / "app/sitemap.ts").read_bytes().replace(b"\r\n", b"\n")
        self.assertEqual(observed, baseline.replace(
            b'const lastModified = "2026-10-15";',
            b'const lastModified = "2026-10-16";', 1))
        self.assertEqual(observed.count(b'universeRoutes.includes(route) ? "2026-10-15" : lastModified'), 1)

    def test_existing_form_and_r7c_guards(self):
        result = profile.check_release()
        for locale, rel in (("ru", "start.html"), ("en", "en/start.html")):
            raw = (builder.LIVE / rel).read_bytes()
            self.assertEqual(raw.count(b'type="submit" disabled'), 1)
            self.assertEqual(raw.count(b'data-lead-state="unready"'), 1)
            self.assertEqual(raw.count(b'src="/lead-form-runtime.js"'), 1)
        self.assertIn(b"const ENABLED = false;", (builder.LIVE / "phuket-universe-events.js").read_bytes())
        self.assertEqual(result["changed_static"], ["sitemap.xml", "_release.json"])

    def test_reject_normal_route_sitemap_tamper(self):
        old = (builder.LIVE / "sitemap.xml").read_bytes()
        mutated = old.replace(
            b'<loc>https://aiskillab.work/</loc><lastmod>2026-10-16</lastmod>',
            b'<loc>https://aiskillab.work/</loc><lastmod>2026-10-15</lastmod>', 1)
        self.assertNotEqual(old, mutated)
        with self.assertRaisesRegex(ValueError, "asset_byte_drift"):
            profile.check_release({"sitemap.xml": mutated})

    def test_reject_universe_lastmod_tamper(self):
        old = (builder.LIVE / "sitemap.xml").read_bytes()
        mutated = old.replace(
            b'<loc>https://aiskillab.work/phuket-universe</loc><lastmod>2026-10-15</lastmod>',
            b'<loc>https://aiskillab.work/phuket-universe</loc><lastmod>2026-10-16</lastmod>', 1)
        self.assertNotEqual(old, mutated)
        with self.assertRaisesRegex(ValueError, "asset_byte_drift"):
            profile.check_release({"sitemap.xml": mutated})

    def test_reject_manifest_lineage_rewrite(self):
        m = json.loads((builder.LIVE / "_release.json").read_bytes())
        m["parent_manifest_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "asset_byte_drift"):
            profile.check_release({"_release.json": json.dumps(m).encode("utf-8")})

    def test_reject_added_unapproved_asset(self):
        with self.assertRaisesRegex(ValueError, "asset_inventory_drift"):
            profile.check_release({"injected.txt": b"UNAPPROVED"})

    def test_reject_deleted_live_asset(self):
        with self.assertRaisesRegex(ValueError, "asset_inventory_drift"):
            profile.check_release({"phuket-universe-events.js": None})

    def test_reject_modified_live_html(self):
        page = (builder.LIVE / "start.html").read_bytes()
        with self.assertRaisesRegex(ValueError, "asset_byte_drift"):
            profile.check_release({"start.html": page + b" "})


def run_units() -> None:
    cases = unittest.defaultTestLoader.loadTestsFromTestCase(SitemapR2Tests)
    result = unittest.TextTestRunner(verbosity=1).run(cases)
    if not result.wasSuccessful():
        raise ValueError("R31_SITEMAP_R2_TESTS_HOLD")
    print("R31_SITEMAP_R2_NEGATIVE_UNITS_PASS cases=12 network_calls=0 production_authority=false")


if __name__ == "__main__":
    run_units()
