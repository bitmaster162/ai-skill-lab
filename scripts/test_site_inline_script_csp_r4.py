#!/usr/bin/env python3
"""16 offline CSP parser and current immutable release regressions (R3.1/R7C/R2)."""
from __future__ import annotations

import base64
import hashlib
import json
import unittest
from pathlib import Path

from site_inline_script_csp_r3 import inline_script_hashes
import subprocess
import build_site_r31_sitemap_r2 as build
import site_r31_sitemap_r2_profile as profile


ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy/live"


def digest(text: str) -> str:
    return "'sha256-" + base64.b64encode(hashlib.sha256(text.encode("utf-8")).digest()).decode("ascii") + "'"


class CodeQLHtmlFilterTests(unittest.TestCase):
    def test_lowercase_and_mixed_case_script_tags(self):
        text = 'window.x = "<tag>";'
        for markup in ("<script>{}</script>", "<SCRIPT>{}</SCRIPT>",
                       "<ScRiPt>{}</sCrIpT>", "<SCRIPT>{}</script>"):
            self.assertEqual(inline_script_hashes(markup.format(text)), {digest(text)})

    def test_mixed_case_src_is_external(self):
        for attr in ('SRC="/safe.js"', 'SrC="/safe.js"', 'src="/safe.js"',
                     "SRC = '/safe.js'", "SRC"):
            self.assertEqual(inline_script_hashes("<ScRiPt " + attr + ">evil()</sCrIpT>"), set())

    def test_attribute_name_must_be_src_not_suffix_or_body(self):
        for attr in ('DATA-SRC="/ignored"', 'srcset="/ignored"', 'x-src="/ignored"'):
            self.assertEqual(inline_script_hashes("<SCRIPT " + attr + ">safe()</SCRIPT>"),
                             {digest("safe()")})
        self.assertEqual(inline_script_hashes("<SCRIPT>const s = 'src=/evil';</SCRIPT>"),
                         {digest("const s = 'src=/evil';")})

    def test_quoted_greater_than_and_inline_raw_utf8(self):
        text = 'const x = ">";\r\nconst pi = "π"; &raw;'
        html = '<ScRiPt data-test="a > b" TyPe="application/ld+json">' + text + '</ScRiPt>'
        self.assertEqual(inline_script_hashes(html), {digest(text)})

    def test_scripts_inside_comments_and_escaped_text_ignored(self):
        html = '<!-- <SCRIPT>doNotHash()</SCRIPT> -->&lt;script&gt;notARealScript&lt;/script&gt;'
        self.assertEqual(inline_script_hashes(html), set())

    def test_empty_and_external_scripts_ignored(self):
        self.assertEqual(inline_script_hashes('<script> \n\t </script><script src="a.js">inlineIgnored</script>'),
                         set())

    def test_distinct_scripts_and_deduplication(self):
        s = '<script>A()</script><SCRIPT>B()</SCRIPT><script>A()</script>'
        self.assertEqual(inline_script_hashes(s), {digest("A()"), digest("B()")})

    def test_scripture_tag_not_script(self):
        self.assertEqual(inline_script_hashes('<scripture>A()</scripture>'), set())

    def test_malformed_unclosed_script_rejected(self):
        with self.assertRaisesRegex(ValueError, "unclosed"):
            inline_script_hashes("<SCRIPT>unclosed()")

    def test_malformed_stray_end_rejected(self):
        with self.assertRaisesRegex(ValueError, "unmatched"):
            inline_script_hashes("</SCRIPT>")

    def test_malformed_self_closing_rejected(self):
        with self.assertRaisesRegex(ValueError, "self-closing"):
            inline_script_hashes("<SCRIPT />")

    def test_not_text_rejected(self):
        with self.assertRaises(TypeError):
            inline_script_hashes(b"<script>code()</script>")  # type: ignore[arg-type]

    def test_all_108_sealed_assets_and_exact_csp(self):
        raw = (LIVE / "_release.json").read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         "fc57c61c7ac502644665f7cc06152f43fb0b5d7f67827eb6fd4b12aadfc83f37")
        manifest = json.loads(raw)
        self.assertEqual(manifest["release_id"], "PHUKET_UNIVERSE_U3_E38_DORMANT_R7B_20261015")
        self.assertEqual(manifest["patch_id"], "SITE_FORM_METADATA_R31_POST_R7C_SITEMAP_20261016_LOCAL_R2")
        self.assertEqual(manifest["file_count"], 108)
        self.assertEqual(len(manifest["files"]), 108)
        self.assertEqual(len([p for p in LIVE.rglob("*") if p.is_file()]), 109)
        report = profile.check_release()
        self.assertEqual((report["assets"], report["routes"]), (108, 56))
        self.assertFalse(report["production_authority"])
        hashes = set()
        for path in LIVE.rglob("*.html"):
            hashes.update(inline_script_hashes(path.read_text("utf-8")))
        rules = json.loads((LIVE / "vercel.json").read_text("utf-8"))["headers"]
        headers = {h["key"]: h["value"] for rule in rules if rule["source"] == "/(.*)"
                   for h in rule["headers"]}
        csp = headers["Content-Security-Policy"]
        self.assertTrue(hashes)
        self.assertTrue(all(value in csp for value in hashes))
        self.assertIn("form-action 'none'", csp)
        self.assertNotIn("'unsafe-inline'", csp)
        self.assertNotIn("'unsafe-eval'", csp)

    def test_current_and_historical_source_blobs_are_immutable(self):
        def git(*args: str) -> str:
            result = subprocess.run(["git", "--no-optional-locks", "-C", str(ROOT), *args],
                                    check=True, capture_output=True, timeout=20)
            return result.stdout.decode("utf-8").strip()
        current = "022bb6bd814d1c6600876aca1d8722f5caf1405f"
        historical = "0f1422eb67aac4855c7d5561e92832fd859cf4e1"
        self.assertEqual(git("rev-parse", current + "^{tree}"),
                         "de7c4330b1ac916a1439fe714b9823c4265cf306")
        self.assertEqual(git("rev-parse", historical + "^{tree}"),
                         "33e66cc859847339cf8494a9154ed6ca82c694cc")
        for rel, blob in {
            "scripts/site_inline_script_csp_r3.py": "f8e4a6afb65b6e070cd2d46c967c49f40efc0ee3",
            "components/LeadForm.tsx": "ac2c3e174e5d168aee47c03e7763c34244a4d627",
            "public/lead-form-runtime.js": "46affb8695cc83a5517f5727be9320ce8544a62b",
        }.items():
            self.assertEqual(git("hash-object", str(ROOT / rel)), blob)
            for rev in (historical, current):
                self.assertIn(blob, git("ls-tree", rev, "--", rel))
        self.assertNotEqual(
            json.loads((LIVE / "_release.json").read_bytes())["release_id"],
            "SITE_FORM_READINESS_CANDIDATE_R1_20261014")

    def test_current_release_rejects_csp_and_manifest_tampering(self):
        raw_csp = (LIVE / "vercel.json").read_bytes()
        self.assertIn(b"form-action 'none'", raw_csp)
        tampered = raw_csp.replace(b"form-action 'none'", b"form-action 'self'", 1)
        with self.assertRaisesRegex(ValueError, "asset_byte_drift"):
            profile.check_release({"vercel.json": tampered})
        old_manifest = (LIVE / "_release.json").read_bytes()
        outdated = json.loads(old_manifest)
        outdated["release_id"] = "SITE_FORM_READINESS_CANDIDATE_R1_20261014"
        with self.assertRaisesRegex(ValueError, "asset_byte_drift"):
            profile.check_release({"_release.json": json.dumps(outdated).encode("utf-8")})
        start = (LIVE / "start.html").read_bytes()
        with self.assertRaisesRegex(ValueError, "asset_byte_drift"):
            profile.check_release({"start.html": start + b"<script>malicious()</script>"})

    def test_current_regeneration_and_parent_immutable(self):
        original = {p.relative_to(LIVE).as_posix(): p.read_bytes()
                    for p in LIVE.rglob("*") if p.is_file()}
        rebuilt, receipt = build.render()
        self.assertEqual(rebuilt, original)
        self.assertEqual(receipt["manifest_sha256"], build.EXPECTED_MANIFEST_SHA)
        self.assertEqual(receipt["payload_sha256"], build.EXPECTED_PAYLOAD_SHA)
        self.assertEqual(len(original), 109)
        parent, old = build.parent_files()
        self.assertEqual(len(parent), 109)
        self.assertEqual(old["file_count"], 108)
        self.assertEqual(build.sha(parent["_release.json"]), build.PARENT_MANIFEST_SHA)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(CodeQLHtmlFilterTests)
    )
    if not result.wasSuccessful():
        raise SystemExit(1)
    print("SITE_R4_CSP_PORT_PASS fixtures=16 release_assets=108 network_calls=0 production_authority=false")
