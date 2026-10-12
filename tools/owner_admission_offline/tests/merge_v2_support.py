"""Independent synthetic merge fixtures: no real owner key or live provider."""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import json
import os
import tempfile

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from owner_admission.canonical import canonical_bytes, canonical_sha256, sha256_bytes
from owner_admission.merge_v2 import (
    ACTION, DOMAIN, MERGE_CONTEXT, MERGE_METHOD, POLICY_VERSION,
    PROHIBITED_EFFECTS, REVIEW_MODE, SCHEMA, SYNTHETIC_SOURCE,
    evaluate_merge_only,
)
from owner_admission.merge_v2_contracts import (
    SyntheticOwnerRegistry, SyntheticMergePolicy, SyntheticProviderSnapshot,
    SyntheticCheck, SyntheticPreview, SyntheticBranchRule, SyntheticLease,
)
from owner_admission.merge_v2_ledger import (
    SyntheticMergeLedger, bootstrap_synthetic_merge_ledger,
)
from tests.support import BASE, BASE_TREE, HEAD, HEAD_TREE, COORD_REF, PATHS

NOW = datetime(2026, 10, 12, 13, 1, 0, tzinfo=timezone.utc)
JIT_NOW = NOW + timedelta(seconds=60)
OWNER_ID = "synthetic-merge-owner-v2"
NONCE = "abcf0123456789ab0123456789abcdef"
LEDGER_ID = "synthetic-ledger-r4f7h-v2"
REGISTRY_VERSION = "synthetic-owner-registry-v2"
CI_APPS = {"static-release": 33001, "language-parity": 33002, "CodeQL": 33003}
MERGE_APP = 44001
PREVIEWS = ("synthetic-public-preview", "synthetic-ingress-preview")
PATCH = b"SYNTHETIC-MERGE-V2-PATCH-BYTES"
EVIDENCE = b"SYNTHETIC-INDEPENDENT-PROVIDER-EVIDENCE-BYTES"


class MergeFixture:
    def __init__(self):
        self.dir = tempfile.TemporaryDirectory(prefix="r4f7h-synthetic-only-")
        # Ephemeral test key in memory, NEVER an owner signing key.
        self.private = Ed25519PrivateKey.generate()
        pub = self.private.public_key().public_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
        self.registry = SyntheticOwnerRegistry(
            {OWNER_ID: pub}, frozenset(), MERGE_APP, REGISTRY_VERSION)
        self.policy = SyntheticMergePolicy(
            "bitmaster162/ai-skill-lab", 226, "main", POLICY_VERSION, PATHS,
            CI_APPS, PREVIEWS, False, max_ttl_seconds=600,
            max_future_skew_seconds=15, max_provider_age_seconds=120,
            max_patch_bytes=200_000, max_evidence_bytes=200_000,
            ledger_id=LEDGER_ID)
        self.payload = dict(
            schema=SCHEMA, policy_version=POLICY_VERSION,
            owner_registry_version=REGISTRY_VERSION, issuer_key_id=OWNER_ID,
            repo=self.policy.repo, pr=226, base_branch="main",
            merge_method=MERGE_METHOD, action=ACTION, base_commit=BASE,
            base_tree=BASE_TREE, head_commit=HEAD, head_tree=HEAD_TREE,
            patch_sha256=sha256_bytes(PATCH), evidence_sha256=sha256_bytes(EVIDENCE),
            allowed_paths_digest=canonical_sha256(sorted(PATHS)),
            coordination_ref_sha=COORD_REF,
            issued_at_utc="2026-10-12T13:00:00Z",
            expires_at_utc="2026-10-12T13:10:00Z",
            nonce=NONCE, review_mode=REVIEW_MODE,
            required_merge_context=MERGE_CONTEXT,
            prohibited_effects=dict(PROHIBITED_EFFECTS),
        )
        required={**CI_APPS, MERGE_CONTEXT: MERGE_APP}
        rule = SyntheticBranchRule(
            "main", True, True, True, True, True, True, False, False,
            False, False, ("merge",), required)
        checks = tuple(SyntheticCheck(k, v, HEAD, "completed", "success", "pull_request")
                       for k, v in CI_APPS.items())
        self.provider = SyntheticProviderSnapshot(
            SYNTHETIC_SOURCE, self.policy.repo, 226, "main", BASE, BASE_TREE,
            HEAD, HEAD_TREE, "OPEN", False, True, "2026-10-12T13:01:00Z",
            PATHS, PATCH, EVIDENCE, checks,
            tuple(SyntheticPreview(v, HEAD, "READY") for v in PREVIEWS),
            rule, SyntheticLease(COORD_REF, "2026-10-12T13:15:00Z",
                                 self.policy.repo, 226, HEAD, ACTION, True),
        )
        self.ledger_path = os.path.join(self.dir.name, "ledger.sqlite")
        bootstrap_synthetic_merge_ledger(self.ledger_path, LEDGER_ID, test_mode=True)
        self.ledger = SyntheticMergeLedger(self.ledger_path, LEDGER_ID)
        self.preissue()

    def envelope(self, overrides=None):
        p = {**self.payload, **(overrides or {})}
        signed = self.private.sign(DOMAIN + canonical_bytes(p))
        return canonical_bytes({"payload": p, "signature_hex": signed.hex()})

    def preissue(self, overrides=None, action=ACTION, **kwargs):
        p = {**self.payload, **(overrides or {})}
        self.ledger.preissue_for_test(
            issuer_key_id=p["issuer_key_id"], nonce=p["nonce"],
            repo=p["repo"], pr=p["pr"], action=action,
            payload_sha256=canonical_sha256(p), base_commit=p["base_commit"],
            head_commit=p["head_commit"],
            expires_at_utc=p["expires_at_utc"], test_mode=True, **kwargs)

    def evaluate(self, *, envelope=None, registry=None, policy=None, provider=None,
                 ledger=None, now=None, phase="PREPARE", action=ACTION):
        return evaluate_merge_only(
            envelope if envelope is not None else self.envelope(),
            registry=self.registry if registry is None else registry,
            policy=self.policy if policy is None else policy,
            provider=self.provider if provider is None else provider,
            ledger=self.ledger if ledger is None else ledger,
            now_utc=NOW if now is None else now,
            requested_action=action, phase=phase)

    def check(self, payload=None, *, app_id=MERGE_APP,
              head_commit=HEAD, external_id=None, status="completed",
              conclusion="success", event="pull_request", run_id=777,
              completed_at="2026-10-12T13:01:30Z"):
        p = payload or self.payload
        return SyntheticCheck(
            MERGE_CONTEXT, app_id, head_commit, status, conclusion, event,
            check_run_id=run_id,
            external_id=external_id if external_id is not None else
            f"{MERGE_CONTEXT}:v2:{canonical_sha256(p)}",
            completed_at_utc=completed_at)

    def after_prepare(self):
        r = self.evaluate()
        assert r.status == "TEST_ONLY_PASS" and r.nonce_consumed
        return replace(self.provider,
                       observed_at_utc="2026-10-12T13:02:00Z",
                       check_runs=self.provider.check_runs + (self.check(),))

    def close(self):
        self.dir.cleanup()
