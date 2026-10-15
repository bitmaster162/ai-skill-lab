#!/usr/bin/env python3
"""CI-only PR232 fetch-depth repair: exact old/new SHA and negative tests.

All tests are strictly local and read-only. No GitHub Actions rerun or remote
writes are performed. The previous R7B manifest/profile and source history are
immutable. A full-history checkout is required because the approved R7B
release verifier performs git show on pinned predecessor commits.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

import phuket_universe_r7b_release_profile as seal

class U3R7BCiFetchDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = seal.git_blob(seal.CI_PARENT_HEAD, seal.CI_WORKFLOW)
        cls.current = (seal.ROOT / seal.CI_WORKFLOW).read_bytes()
        cls.sealed_profile = json.loads(seal.PROFILE_PATH.read_bytes())

    def assertDenied(self, proposal: bytes, baseline: bytes | None = None):
        with self.assertRaises(ValueError):
            seal.prove_ci_fetch_depth_repair(proposal, baseline)

    def test_original_history_is_independently_pinned(self):
        self.assertEqual(seal.sha(self.original), seal.CI_ORIGINAL_SHA)
        self.assertEqual(self.sealed_profile["source_override_sha256"][seal.CI_WORKFLOW],
                         seal.CI_ORIGINAL_SHA)
        self.assertEqual(self.original.count(seal.CI_CHECKOUT_LINE), 1)
        self.assertNotIn(b"fetch-depth:", self.original)

    def test_exact_additive_workflow_only(self):
        self.assertEqual(seal.prove_ci_fetch_depth_repair(self.current), seal.CI_REPAIRED_SHA)
        self.assertEqual(seal.sha(self.current), seal.CI_REPAIRED_SHA)
        self.assertEqual(len(self.current) - len(self.original), 39)
        self.assertEqual(self.current.replace(
            seal.CI_CHECKOUT_LINE+seal.CI_FETCH_DEPTH_SETTING,
            seal.CI_CHECKOUT_LINE, 1), self.original)
        self.assertEqual(self.current.count(b"      - uses: actions/checkout@"), 1)

    def test_original_shallow_workflow_rejected(self):
        self.assertDenied(self.original)

    def test_shallow_fetch_depth_one_rejected(self):
        self.assertDenied(self.current.replace(b"fetch-depth: 0",b"fetch-depth: 1",1))

    def test_incorrect_fetch_depth_two_rejected(self):
        self.assertDenied(self.current.replace(b"fetch-depth: 0",b"fetch-depth: 2",1))

    def test_doubled_fetch_depth_rejected(self):
        self.assertDenied(self.current.replace(
            b"          fetch-depth: 0\n",
            b"          fetch-depth: 0\n          fetch-depth: 0\n",1))

    def test_inline_checkout_fetch_depth_rejected(self):
        self.assertDenied(self.current.replace(
            b"        with:\n          fetch-depth: 0\n",
            b"        with: {fetch-depth: 0}\n",1))

    def test_added_persist_credentials_rejected(self):
        self.assertDenied(self.current.replace(
            b"          fetch-depth: 0\n",
            b"          fetch-depth: 0\n          persist-credentials: true\n",1))

    def test_setup_python_version_drift_rejected(self):
        self.assertDenied(self.current.replace(b"python-version: '3.12'",
                                               b"python-version: '3.13'",1))

    def test_checkout_action_sha_drift_rejected(self):
        self.assertDenied(self.current.replace(
            b"3d3c42e5aac5ba805825da76410c181273ba90b1",
            b"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",1))

    def test_unrelated_workflow_modification_rejected(self):
        self.assertDenied(self.current+b"# unapproved footer\n")

    def test_manipulated_baseline_sha_rejected(self):
        self.assertDenied(self.current, self.original+b"# forged\n")

    def test_invalid_candidate_type_rejected(self):
        self.assertDenied("not bytes")  # type: ignore[arg-type]

    def test_original_sealed_profile_is_unchanged(self):
        raw=seal.PROFILE_PATH.read_bytes()
        self.assertEqual(seal.sha(raw),seal.PROFILE_SHA)
        self.assertEqual(seal.PROFILE_SHA,
                         "4bb0b241618a3d75aee2de39ffd1771279e4d13399e00af2fa45661e57b26d39")
        approved=seal.profile()
        self.assertEqual(approved["source_override_sha256"][seal.CI_WORKFLOW],
                         seal.CI_REPAIRED_SHA)
        self.assertEqual(self.sealed_profile["source_override_sha256"][seal.CI_WORKFLOW],
                         seal.CI_ORIGINAL_SHA)
        self.assertEqual(approved["authority"], seal.AUTHORITY)
        self.assertFalse(any(approved["authority"].values()))

    def test_published_content_is_frozen_to_r7b_parent(self):
        for path in ("deploy/live/_release.json",
                     "data/phuket_universe_u3_e38_r7b_profile.json",
                     "deploy/live/sitemap.xml",
                     "deploy/live/phuket-universe-events.js",
                     "schema/public_event_daily_e38.sql",
                     "services/lead-ingress/api/event.js",
                     "services/lead-receiver-cloudflare/src/index.js",
                     "package-lock.json"):
            with self.subTest(path=path):
                self.assertEqual((seal.ROOT/path).read_bytes(),
                                 seal.git_blob(seal.CI_PARENT_HEAD,path))

def run_units():
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(U3R7BCiFetchDepthTests)
    result=unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():
        raise ValueError("U3 R7B CI fetch-depth bounded repair acceptance failed")

if __name__ == "__main__":
    run_units()
    print("R7B_CI_FETCH_DEPTH_REPAIR_TARGETED_PASS")
