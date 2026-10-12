"""SYNTHETIC ONLY: ephemeral in-memory signing keys and fake provider facts.

The test suite never serializes private key bytes or writes signer keys to disk.
Synthetic check App IDs do NOT identify live GitHub integrations.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import tempfile
import sqlite3

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from owner_admission.canonical import DOMAIN, canonical_bytes, canonical_sha256, sha256_bytes
from owner_admission.contracts import (
    BranchRule, CheckRun, LeaseEvidence, Preview, ProviderSnapshot, TestPolicy,
    TrustRegistry,
)
from owner_admission.ledger import SqliteNonceLedger, bootstrap_test_ledger
from owner_admission.verifier import LIMITS, POLICY_VERSION, ACTION

BASE = "0ab438a2568e562603b707c377c91bee1c836a8a"
BASE_TREE = "7eaced40ab4b21c621d37b072d1558343574a801"
HEAD = "c4dc530b1c62694c6c8f9dbac25bf9d26c46d690"
HEAD_TREE = "2848b8684ea8766d52195e958e98983ae42bcffd"
COORD_REF = "6087e59afff11b8529dcf87e983cc8cf5505df1a"
EVIDENCE = b"SYNTHETIC-SPARK-EVIDENCE-BYTES-TEST-ONLY"
PATCH = b"SYNTHETIC-PR-DIFF-BYTES-TEST-ONLY"
PATHS = (
    ".github/workflows/static-qa.yml",
    "release_admission/__init__.py",
    "release_admission/authority.py",
    "release_admission/baseline.py",
    "release_admission/validator.py",
    "scripts/check_preflight_safety.py",
    "scripts/check_qa_gate_inventory.py",
    "scripts/check_release_profile_admission.py",
    "scripts/preflight_release.py",
    "scripts/test_release_profile_admission.py",
)
NOW = datetime(2026, 10, 12, 13, 1, 0, tzinfo=timezone.utc)
CI_APPS = {"static-release": 11101, "language-parity": 11102, "CodeQL": 11103}
OWNER_APP_ID = 22201
PREVIEWS = ("synthetic-public-project", "synthetic-ingress-project")
KEY_ID = "synthetic-test-key-v1"


class Fixture:
    def __init__(self):
        # No owner key generated. Every test uses one ephemeral *synthetic* key.
        self.private = Ed25519PrivateKey.generate()
        pub = self.private.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw)
        self.registry = TrustRegistry({KEY_ID: pub}, frozenset(), OWNER_APP_ID,
                                      "synthetic-registry-r1")
        self.policy = TestPolicy(
            "bitmaster162/ai-skill-lab", 226, POLICY_VERSION, PATHS, CI_APPS,
            PREVIEWS, max_ttl_seconds=900, max_future_skew_seconds=15,
            max_provider_age_seconds=120,
            max_patch_bytes=4_000_000, max_evidence_bytes=4_000_000)
        self.payload = dict(
            schema="ai-skill-lab.owner-admission.v1",
            policy_version=POLICY_VERSION,
            issuer_key_id=KEY_ID,
            repo="bitmaster162/ai-skill-lab",
            pr=226,
            action=ACTION,
            base_commit=BASE,
            base_tree=BASE_TREE,
            head_commit=HEAD,
            head_tree=HEAD_TREE,
            evidence_sha256=sha256_bytes(EVIDENCE),
            allowed_paths_digest=canonical_sha256(sorted(PATHS)),
            patch_sha256=sha256_bytes(PATCH),
            issued_at_utc="2026-10-12T13:00:00Z",
            expires_at_utc="2026-10-12T13:10:00Z",
            nonce="0123456789abcdef0123456789abcdef",
            review_mode="SOURCE_ONLY_NO_RELEASE",
            coordination_ref_sha=COORD_REF,
            limits=dict(LIMITS),
        )
        self.provider = ProviderSnapshot(
            repo=self.payload["repo"], pr=226, base_commit=BASE,
            base_tree=BASE_TREE, head_commit=HEAD, head_tree=HEAD_TREE,
            state="OPEN", draft=True, observed_at_utc="2026-10-12T13:00:45Z",
            changed_paths=PATHS, raw_patch=PATCH, raw_evidence=EVIDENCE,
            check_runs=tuple(CheckRun(n, app, HEAD, "completed", "success", "pull_request")
                             for n, app in CI_APPS.items()),
            previews=tuple(Preview(p, "READY", HEAD) for p in PREVIEWS),
            rule=BranchRule(True, True, True, True, True, True, False, False,
                            False, {**CI_APPS, "owner-admission": OWNER_APP_ID}),
            lease=LeaseEvidence(COORD_REF, "2026-10-12T13:11:00Z",
                                self.payload["repo"], HEAD, ACTION, True),
        )
        self.dir = tempfile.TemporaryDirectory(prefix="r4f7f-test-ledger-")
        ledger_path = str(Path(self.dir.name) / "nonce-test.db")
        bootstrap_test_ledger(ledger_path, test_mode=True)
        # Synthetic issuance commitment. Real issuance must be an independent
        # authenticated service with its own custody and audit trail.
        conn=sqlite3.connect(ledger_path)
        try:
            conn.execute("INSERT INTO issued VALUES (?, ?, ?, ?, ?, ?)",
                         (KEY_ID, self.payload["nonce"], canonical_sha256(self.payload),
                          ACTION, HEAD, self.payload["expires_at_utc"]))
            conn.commit()
        finally:
            conn.close()
        self.ledger = SqliteNonceLedger(ledger_path)

    def cleanup(self):
        self.dir.cleanup()

    def envelope(self, payload=None, *, private=None):
        p = self.payload if payload is None else payload
        k = self.private if private is None else private
        sign = k.sign(DOMAIN + canonical_bytes(p)).hex()
        return canonical_bytes({"payload": p, "signature_hex": sign})
