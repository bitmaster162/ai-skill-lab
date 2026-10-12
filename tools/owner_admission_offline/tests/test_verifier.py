"""Negative-test suite: verifies fail-closed offline contract, NOT production."""
from dataclasses import replace
from datetime import timedelta
import copy
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from owner_admission.canonical import canonical_bytes
from owner_admission.contracts import CheckRun, Preview, TrustRegistry
from owner_admission.verifier import evaluate
from tests.support import (
    BASE, CI_APPS, COORD_REF, EVIDENCE, Fixture, HEAD, HEAD_TREE,
    KEY_ID, NOW, PATCH, PATHS, PREVIEWS,
)


class OfflineGateTest(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()

    def tearDown(self):
        self.f.cleanup()

    def run_gate(self, *, doc=None, provider=None, registry=None, policy=None,
                 ledger=None, now=None, action="MARK_READY_ONLY"):
        return evaluate(self.f.envelope() if doc is None else doc,
                        registry=self.f.registry if registry is None else registry,
                        policy=self.f.policy if policy is None else policy,
                        provider=self.f.provider if provider is None else provider,
                        ledger=self.f.ledger if ledger is None else ledger,
                        now_utc=NOW if now is None else now, requested_action=action)

    def signed_mutation(self, **changes):
        p=copy.deepcopy(self.f.payload)
        p.update(changes)
        return self.f.envelope(p)

    def check_failure(self, code, **kwargs):
        verdict=self.run_gate(**kwargs)
        self.assertEqual(verdict.code,code)
        self.assertNotEqual(verdict.status,"TEST_ONLY_PASS")
        self.assertFalse(verdict.nonce_consumed)
        self.assertFalse(verdict.eligible_for_real_action)
        self.assertFalse(verdict.github_check_publishable)
        self.assertFalse(verdict.merge_authorized)
        self.assertFalse(verdict.production_publish_authorized)

    def test_positive_is_only_offline_contract(self):
        v=self.run_gate()
        self.assertEqual((v.status,v.code),("TEST_ONLY_PASS","PASS_OFFLINE_CONTRACT_ONLY"))
        self.assertTrue(v.nonce_consumed)
        self.assertTrue(v.test_only)
        self.assertFalse(v.eligible_for_real_action)
        self.assertFalse(v.github_check_publishable)
        self.assertFalse(v.merge_authorized)
        self.assertFalse(v.production_publish_authorized)

    def test_nonce_cannot_be_replayed(self):
        self.assertEqual(self.run_gate().status,"TEST_ONLY_PASS")
        self.check_failure("DENY_REPLAYED_NONCE")

    def test_negative_does_not_consume_nonce(self):
        bad=replace(self.f.provider,previews=())
        self.check_failure("HOLD_REQUIRED_PREVIEW_MISSING",provider=bad)
        self.assertEqual(self.run_gate().status,"TEST_ONLY_PASS")

    def test_duplicate_json_field_rejected(self):
        raw=self.f.envelope()
        self.check_failure("DENY_MALFORMED_ENVELOPE",doc=raw.replace(b'"payload":',b'"payload":{},"payload":',1))

    def test_float_and_nan_rejected(self):
        for doc in (b'{"payload":{},"signature_hex":NaN}',b'{"payload":{},"signature_hex":1.5}'):
            with self.subTest(doc=doc):
                self.check_failure("DENY_MALFORMED_ENVELOPE",doc=doc)

    def test_extra_signed_field_denied(self):
        p=copy.deepcopy(self.f.payload)
        p["allow_override"]=True
        self.check_failure("DENY_PAYLOAD_FIELDS",doc=self.f.envelope(p))

    def test_unknown_key_id_denied(self):
        self.check_failure("DENY_OWNER_KEY_NOT_PINNED",doc=self.signed_mutation(issuer_key_id="unknown-key-v1"))

    def test_revoked_key_denied(self):
        r=replace(self.f.registry,revoked_owner_key_ids=frozenset({KEY_ID}))
        self.check_failure("DENY_REVOKED_OWNER_KEY",registry=r)

    def test_owner_registry_not_installed_holds(self):
        r=replace(self.f.registry,owner_public_keys={})
        self.check_failure("HOLD_EXTERNAL_ROOT_NOT_INSTALLED",registry=r)

    def test_wrong_signature_denied(self):
        other=Ed25519PrivateKey.generate()  # synthetic in-memory test only
        self.check_failure("DENY_ED25519_SIGNATURE",doc=self.f.envelope(private=other))

    def test_attestation_for_merge_never_authorizes(self):
        self.check_failure("DENY_ACTION_NOT_IN_OFFLINE_SCOPE",action="MERGE_ONLY")
        self.check_failure("DENY_UNSUPPORTED_ACTION_OR_REVIEW_MODE",doc=self.signed_mutation(action="MERGE_ONLY"))

    def test_attestation_with_nonzero_limits_denied(self):
        p=copy.deepcopy(self.f.payload)
        p["limits"]["merge"]=True
        self.check_failure("DENY_NONZERO_EFFECT_SCOPE",doc=self.f.envelope(p))

    def test_wrong_repository_denied(self):
        self.check_failure("STOP_POLICY_TARGET_MISMATCH",doc=self.signed_mutation(repo="attacker/ai-skill-lab"))

    def test_wrong_pr_denied(self):
        self.check_failure("STOP_POLICY_TARGET_MISMATCH",doc=self.signed_mutation(pr=227))

    def test_head_commit_drift_stops(self):
        self.check_failure("STOP_SHA_OR_TREE_DRIFT",doc=self.signed_mutation(head_commit="a"*40))

    def test_base_tree_drift_stops(self):
        self.check_failure("STOP_SHA_OR_TREE_DRIFT",doc=self.signed_mutation(base_tree="b"*40))

    def test_patch_tamper_denied(self):
        bad=replace(self.f.provider,raw_patch=PATCH+b"tampered")
        self.check_failure("DENY_PATCH_SHA256_DRIFT",provider=bad)

    def test_evidence_tamper_denied(self):
        bad=replace(self.f.provider,raw_evidence=EVIDENCE+b"tampered")
        self.check_failure("DENY_EVIDENCE_SHA256_DRIFT",provider=bad)

    def test_path_inventory_change_denied(self):
        bad=replace(self.f.provider,changed_paths=PATHS[:-1]+("unapproved.py",))
        self.check_failure("DENY_CHANGED_PATH_SCOPE",provider=bad)

    def test_duplicate_paths_denied(self):
        bad=replace(self.f.provider,changed_paths=PATHS+(PATHS[0],))
        self.check_failure("DENY_CHANGED_PATH_INVENTORY",provider=bad)

    def test_path_digest_mismatch_denied(self):
        self.check_failure("DENY_CHANGED_PATH_DIGEST",doc=self.signed_mutation(allowed_paths_digest="1"*64))

    def test_duplicate_push_and_pull_request_checks_holds(self):
        duplicate=CheckRun("static-release",CI_APPS["static-release"],HEAD,"completed","success","push")
        bad=replace(self.f.provider,check_runs=self.f.provider.check_runs+(duplicate,))
        self.check_failure("HOLD_DUPLICATE_CHECK_NAME_AMBIGUITY",provider=bad)

    def test_wrong_app_spoofed_check_denied(self):
        vals=list(self.f.provider.check_runs)
        vals[0]=replace(vals[0],app_id=999)
        self.check_failure("DENY_CI_WRONG_APP_HEAD_OR_EVENT",provider=replace(self.f.provider,check_runs=tuple(vals)))

    def test_wrong_event_check_denied(self):
        vals=list(self.f.provider.check_runs)
        vals[0]=replace(vals[0],event="push")
        self.check_failure("DENY_CI_WRONG_APP_HEAD_OR_EVENT",provider=replace(self.f.provider,check_runs=tuple(vals)))

    def test_required_ci_missing_holds(self):
        self.check_failure("HOLD_REQUIRED_CI_MISSING",provider=replace(self.f.provider,check_runs=self.f.provider.check_runs[:-1]))

    def test_required_ci_failed_holds(self):
        vals=list(self.f.provider.check_runs)
        vals[0]=replace(vals[0],conclusion="failure")
        self.check_failure("HOLD_CI_NOT_SUCCESS",provider=replace(self.f.provider,check_runs=tuple(vals)))

    def test_branch_protection_missing_holds(self):
        self.check_failure("HOLD_PROVIDER_PROTECTION_INSUFFICIENT",provider=replace(self.f.provider,rule=replace(self.f.provider.rule,protected=False)))

    def test_branch_bypass_holds(self):
        self.check_failure("HOLD_PROVIDER_PROTECTION_INSUFFICIENT",provider=replace(self.f.provider,rule=replace(self.f.provider.rule,no_bypass=False)))

    def test_force_push_or_deletion_holds(self):
        for flag in ("allow_force_pushes","allow_deletions"):
            with self.subTest(flag=flag):
                self.check_failure("HOLD_PROVIDER_PROTECTION_INSUFFICIENT",provider=replace(self.f.provider,rule=replace(self.f.provider.rule,**{flag:True})))

    def test_owner_status_not_required_holds(self):
        rule=replace(self.f.provider.rule,required_check_app_ids=dict(CI_APPS))
        self.check_failure("HOLD_TRUSTED_OWNER_STATUS_NOT_REQUIRED",provider=replace(self.f.provider,rule=rule))

    def test_owner_status_wrong_app_id_holds(self):
        required={**CI_APPS,"owner-admission":CI_APPS["static-release"]}
        rule=replace(self.f.provider.rule,required_check_app_ids=required)
        self.check_failure("HOLD_TRUSTED_OWNER_STATUS_NOT_REQUIRED",provider=replace(self.f.provider,rule=rule))

    def test_required_preview_missing_holds(self):
        self.check_failure("HOLD_REQUIRED_PREVIEW_MISSING",provider=replace(self.f.provider,previews=self.f.provider.previews[:-1]))

    def test_canceled_preview_holds(self):
        previews=list(self.f.provider.previews)
        previews[0]=replace(previews[0],state="CANCELED")
        self.check_failure("HOLD_REQUIRED_PREVIEW_NOT_READY",provider=replace(self.f.provider,previews=tuple(previews)))

    def test_preview_wrong_head_holds(self):
        previews=list(self.f.provider.previews)
        previews[0]=replace(previews[0],git_commit=BASE)
        self.check_failure("HOLD_REQUIRED_PREVIEW_NOT_READY",provider=replace(self.f.provider,previews=tuple(previews)))

    def test_duplicate_preview_holds(self):
        duplicated=self.f.provider.previews+(self.f.provider.previews[0],)
        self.check_failure("HOLD_DUPLICATE_PREVIEW_PROJECT",provider=replace(self.f.provider,previews=duplicated))

    def test_expired_lease_holds(self):
        lease=replace(self.f.provider.lease,expires_at_utc="2026-10-12T12:59:00Z")
        self.check_failure("HOLD_COORDINATION_LEASE_NOT_AUTHORIZED",provider=replace(self.f.provider,lease=lease))

    def test_wrong_lease_scope_holds(self):
        lease=replace(self.f.provider.lease,authorized_action="MERGE_ONLY")
        self.check_failure("HOLD_COORDINATION_LEASE_NOT_AUTHORIZED",provider=replace(self.f.provider,lease=lease))

    def test_expired_attestation_denied(self):
        self.check_failure("DENY_ATTESTATION_EXPIRED",now=NOW+timedelta(minutes=20))

    def test_future_issued_at_denied(self):
        self.check_failure("DENY_ISSUED_IN_FUTURE",doc=self.signed_mutation(issued_at_utc="2026-10-12T13:02:00Z"))

    def test_ttl_exceed_budget_denied(self):
        self.check_failure("DENY_ATTESTATION_TTL",doc=self.signed_mutation(expires_at_utc="2026-10-12T13:30:00Z"))

    def test_stale_provider_snapshot_holds(self):
        bad=replace(self.f.provider,observed_at_utc="2026-10-12T12:00:00Z")
        self.check_failure("HOLD_PROVIDER_SNAPSHOT_STALE",provider=bad)

    def test_undrafted_pr_holds(self):
        bad=replace(self.f.provider,draft=False)
        self.check_failure("HOLD_PR_NOT_OPEN_DRAFT",provider=bad)

    def test_unknown_nonce_ledger_holds(self):
        from owner_admission.ledger import SqliteNonceLedger
        import os
        missing=SqliteNonceLedger(os.path.join(self.f.dir.name,"missing.sqlite"))
        self.check_failure("HOLD_INDEPENDENT_LEDGER_UNAVAILABLE",ledger=missing)

    def test_unknown_issuance_commitment_is_denied(self):
        import sqlite3
        db=sqlite3.connect(self.f.ledger.path)
        db.execute("DELETE FROM issued")
        db.commit();db.close()
        self.check_failure("DENY_NONCE_NOT_IN_PREISSUED_LEDGER")

    def test_issuance_commitment_scope_tamper_denied(self):
        import sqlite3
        db=sqlite3.connect(self.f.ledger.path)
        db.execute("UPDATE issued SET head_commit=?", ("f"*40,))
        db.commit();db.close()
        self.check_failure("DENY_NONCE_NOT_IN_PREISSUED_LEDGER")

    def test_no_ledger_holds(self):
        result=evaluate(self.f.envelope(),registry=self.f.registry,policy=self.f.policy,
                        provider=self.f.provider,ledger=None,now_utc=NOW)
        self.assertEqual(result.code,"HOLD_INDEPENDENT_LEDGER_NOT_INSTALLED")
        self.assertFalse(result.nonce_consumed)

    def test_production_mode_always_holds(self):
        pol=replace(self.f.policy,audience="PRODUCTION")
        self.check_failure("HOLD_PRODUCTION_VERIFIER_UNIMPLEMENTED",policy=pol)

    def test_missing_signed_preview_waiver_not_inferred(self):
        self.check_failure("HOLD_REQUIRED_PREVIEW_MISSING",provider=replace(self.f.provider,previews=()))

    def test_actual_ci_green_cannot_self_approve(self):
        self.check_failure("HOLD_EXTERNAL_ROOT_NOT_INSTALLED",registry=replace(self.f.registry,owner_public_keys={}))

    def test_noncanonical_timestamp_denied(self):
        self.check_failure("DENY_TIMESTAMP_FORMAT",doc=self.signed_mutation(
            expires_at_utc="2026-10-12T13:10:00+00:00"))

    def test_invalid_provider_observation_holds(self):
        bad=replace(self.f.provider,observed_at_utc="invalid")
        self.check_failure("HOLD_PROVIDER_TIMESTAMP_BAD",provider=bad)

    def test_invalid_lease_expiry_holds(self):
        lease=replace(self.f.provider.lease,expires_at_utc="invalid")
        self.check_failure("HOLD_LEASE_EXPIRY_INVALID",provider=replace(self.f.provider,lease=lease))

    def test_malformed_provider_contract_denied_without_effect(self):
        bad=replace(self.f.provider,rule=None)
        self.check_failure("DENY_INVALID_CONTRACT",provider=bad)

    def test_evaluation_receipt_serialization_denies_effects(self):
        out=self.run_gate().as_dict()
        self.assertEqual(out["status"], "TEST_ONLY_PASS")
        for key in ("eligible_for_real_action", "merge_authorized",
                    "production_publish_authorized", "github_check_publishable"):
            self.assertIs(out[key],False)

    def test_wrong_signature_hex_encoding_denied(self):
        raw=self.f.envelope()
        bad=raw.replace(b'"signature_hex":"',b'"signature_hex":"zz',1)
        self.check_failure("DENY_SIGNATURE_ENCODING",doc=bad)

    def test_invalid_nonce_encoding_denied(self):
        self.check_failure("DENY_NONCE_FORMAT",doc=self.signed_mutation(nonce="bad"))

    def test_invalid_review_mode_denied(self):
        self.check_failure("DENY_UNSUPPORTED_ACTION_OR_REVIEW_MODE",doc=self.signed_mutation(review_mode="PRODUCTION_RELEASE"))

    def test_wrong_policy_version_denied(self):
        self.check_failure("DENY_SCHEMA_OR_POLICY_VERSION",doc=self.signed_mutation(policy_version="OLD_VERSION"))

    def test_independent_app_must_differ_from_ci_apps(self):
        registry=replace(self.f.registry,independent_app_id=CI_APPS["static-release"])
        self.check_failure("HOLD_OWNER_APP_NOT_INDEPENDENT",registry=registry)

    def test_missing_required_ci_policy_hold(self):
        pol=replace(self.f.policy,required_ci_app_ids={})
        self.check_failure("HOLD_TEST_POLICY_BAD_SCOPE",policy=pol)

    def test_invalid_resource_budgets_hold(self):
        pol=replace(self.f.policy,max_patch_bytes=0)
        self.check_failure("HOLD_TEST_POLICY_BAD_SCOPE",policy=pol)

    def test_evidence_budget_enforced(self):
        pol=replace(self.f.policy,max_evidence_bytes=1)
        self.check_failure("DENY_EVIDENCE_SHA256_DRIFT",policy=pol)

    def test_owner_status_spoof_in_candidate_ci_does_not_count(self):
        # A forged owner-admission GitHub Actions status cannot be the external
        # provider-required rule/App. Even the 'success' label doesn't help.
        forged=CheckRun("owner-admission",CI_APPS["static-release"],HEAD,
                        "completed","success","pull_request")
        rule=replace(self.f.provider.rule,required_check_app_ids={**CI_APPS,"owner-admission":CI_APPS["static-release"]})
        bad=replace(self.f.provider,rule=rule,check_runs=self.f.provider.check_runs+(forged,))
        self.check_failure("HOLD_TRUSTED_OWNER_STATUS_NOT_REQUIRED",provider=bad)


if __name__ == "__main__":
    unittest.main()
