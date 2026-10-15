#!/usr/bin/env python3
"""Offline positive and fail-closed regressions for the R3.1 CodeQL HTML-filter fix."""
from __future__ import annotations

import base64
import hashlib
import json
import unittest
from pathlib import Path

from site_inline_script_csp_r3 import inline_script_hashes
from build_site_release_r3 import inline_hashes, parent_files, render, sha
from verify_site_metadata_preview_r1 import script_hashes


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

    def test_all_99_sealed_assets_and_exact_csp(self):
        manifest = json.loads((LIVE / "_release.json").read_bytes())
        self.assertEqual(manifest["file_count"], 99)
        self.assertEqual(len(manifest["files"]), 99)
        self.assertEqual(sha((LIVE / "_release.json").read_bytes()),
                         "c421131415217f28a99061090be95bd7d75975940ec5251430ab0a96c328e21e")
        h1 = script_hashes(LIVE)
        h2 = inline_hashes({p.relative_to(LIVE).as_posix(): p.read_bytes()
                            for p in LIVE.rglob("*") if p.is_file()})
        self.assertEqual(h1, h2)
        csp = (LIVE / "vercel.json").read_text("utf-8")
        self.assertTrue(h1)
        self.assertTrue(all(value in csp for value in h1))
        self.assertIn("form-action 'none'", csp)
        self.assertNotIn("'unsafe-inline'", csp)

    def test_codeql_repin_is_exact_two_source_delta(self):
        import subprocess
        import site_form_metadata_r3 as profile
        baseline = "938f6f29abdf61e78b382c0ded82e3abe8c02e59"
        record = "data/site_form_metadata_r3_1_pins.json"
        old = subprocess.run(["git", "-C", str(ROOT), "show", baseline + ":" + record],
                             capture_output=True, check=True, timeout=20).stdout
        original = json.loads(old)
        current = json.loads((ROOT / record).read_bytes())
        self.assertEqual(sha(old), "eb3978ee4a69587d0d268e30f3e70da9d196300e244c2fe17797651d11f6f2e4")
        self.assertEqual(sha((ROOT / record).read_bytes()),
                         "1e791f7f4a360b99b7d590c5d33923c798d4bbb1b0bbc2b0dd944c485cff42b8")
        self.assertEqual(profile.load_pins(ROOT), current)
        for field in original:
            if field != "source_sha256_lf":
                self.assertEqual(original[field], current[field], field)
        source_delta = {name for name in original["source_sha256_lf"]
                        if original["source_sha256_lf"][name] != current["source_sha256_lf"][name]}
        self.assertEqual(source_delta, {
            "scripts/build_site_release_r3.py",
            "scripts/verify_site_metadata_preview_r1.py",
        })
        added_sources = set(current["source_sha256_lf"]) - set(original["source_sha256_lf"])
        self.assertEqual(added_sources, {"scripts/site_inline_script_csp_r3.py"})
        self.assertEqual(current["source_sha256_lf"]["scripts/site_inline_script_csp_r3.py"],
                         sha((ROOT / "scripts/site_inline_script_csp_r3.py").read_bytes()))
        for name in source_delta:
            self.assertEqual(
                sha(profile.canonical_source((ROOT / name).read_bytes())),
                current["source_sha256_lf"][name],
            )

    def test_revised_sources_still_fail_closed_on_change(self):
        import site_form_metadata_r3 as profile
        for name in ("scripts/build_site_release_r3.py",
                     "scripts/verify_site_metadata_preview_r1.py",
                     "scripts/site_inline_script_csp_r3.py"):
            mutated = (ROOT / name).read_bytes() + b"\\nCODEQL_NEGATIVE_FIXTURE"
            outcome = profile.validate(ROOT, overrides={name: mutated})
            self.assertTrue(any("exact source: " + name in e for e in outcome["errors"]))
            self.assertFalse(outcome["release_authorization"])

    def test_rebuild_and_immutable_parent(self):
        original = {p.relative_to(LIVE).as_posix(): p.read_bytes()
                    for p in LIVE.rglob("*") if p.is_file()}
        rebuilt = render()
        self.assertEqual(rebuilt, original)
        self.assertEqual(sha(rebuilt["_release.json"]),
                         "c421131415217f28a99061090be95bd7d75975940ec5251430ab0a96c328e21e")
        self.assertEqual(len(parent_files()), 98)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(CodeQLHtmlFilterTests)
    )
    if not result.wasSuccessful():
        raise SystemExit(1)
    print("SITE_R3_CODEQL_HTML_FILTER_PASS fixtures=16 payload_bytes_unchanged=true network_calls=0")
