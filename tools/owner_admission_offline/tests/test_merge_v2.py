"""R4F7H action isolation, CI source, signature and JIT guard regression."""
from __future__ import annotations

from dataclasses import replace
from contextlib import closing
from datetime import datetime, timedelta, timezone
import json
import os
import tempfile
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from owner_admission.canonical import DOMAIN as V1_DOMAIN, canonical_bytes, canonical_sha256
from owner_admission.merge_v2 import (
    ACTION, DOMAIN, MERGE_CONTEXT, POLICY_VERSION, PROHIBITED_EFFECTS,
    SCHEMA, evaluate_merge_only,
)
from owner_admission.merge_v2_contracts import SyntheticCheck
from owner_admission.merge_v2_ledger import SyntheticMergeLedger
from tests.merge_v2_support import (
    MergeFixture, NOW, JIT_NOW, MERGE_APP, CI_APPS, HEAD,
    BASE, BASE_TREE, HEAD_TREE, PATHS, PREVIEWS, NONCE,
)


class TestMergeAction(unittest.TestCase):
    def setUp(self):
        self.f = MergeFixture()
        self.addCleanup(self.f.close)

    def fail_with(self, code, **options):
        r=self.f.evaluate(**options)
        self.assertEqual(r.code, code, r.as_dict())
        self.assertIn(r.status, ("DENY", "HOLD", "STOP"), r.as_dict())
        self.assertFalse(r.merge_authorized)
        self.assertFalse(r.github_check_publishable)
        self.assertFalse(r.production_publish_authorized)
        self.assertFalse(r.execution_action_performed)
        self.assertFalse(r.real_owner_authority)
        return r

    def sign(self, **changes):
        return self.f.envelope(changes)

    def test_prepare_returns_test_only(self):
        r=self.f.evaluate()
        self.assertEqual((r.status,r.code,r.phase),
                         ("TEST_ONLY_PASS","PASS_SYNTHETIC_CHECK_PREPARE_ONLY","PREPARE"))
        self.assertTrue(r.nonce_consumed)
        self.assertFalse(r.independently_authenticated_provider)
        for key in ("real_owner_authority","github_check_publishable","merge_authorized",
                    "mark_ready_authorized","deploy_authorized","production_publish_authorized",
                    "execution_action_performed"):
            self.assertIs(r.as_dict()[key],False)

    def test_premerge_jit_requires_successful_prepare(self):
        ready=replace(self.f.provider,
                      observed_at_utc="2026-10-12T13:02:00Z",
                      check_runs=self.f.provider.check_runs+(self.f.check(),))
        self.fail_with("HOLD_MERGE_NONCE_CONSUMPTION_NOT_VERIFIED",
                       phase="JIT_EXECUTION",provider=ready,now=JIT_NOW)

    def test_premerge_jit_pass_only_synthetic(self):
        ready=self.f.after_prepare()
        r=self.f.evaluate(phase="JIT_EXECUTION",provider=ready,now=JIT_NOW)
        self.assertEqual(r.status,"TEST_ONLY_PASS")
        self.assertEqual(r.code,"PASS_SYNTHETIC_JIT_REVALIDATION_ONLY")
        self.assertFalse(r.nonce_consumed)
        self.assertFalse(r.github_check_publishable)
        self.assertFalse(r.merge_authorized)

    def test_prior_mark_ready_signature_does_not_authorize_merge(self):
        p={**self.f.payload,"action":"MARK_READY_ONLY"}
        sig=self.f.private.sign(V1_DOMAIN+canonical_bytes(p))
        self.fail_with("DENY_WRONG_ACTION_OR_METHOD",envelope=canonical_bytes(
            {"payload":p,"signature_hex":sig.hex()}))

    def test_wrong_domain_signature_rejected(self):
        p=self.f.payload
        sig=self.f.private.sign(V1_DOMAIN+canonical_bytes(p))
        self.fail_with("DENY_MERGE_SIGNATURE",envelope=canonical_bytes(
            {"payload":p,"signature_hex":sig.hex()}))

    def test_mark_ready_requested_action_rejected(self):
        self.fail_with("DENY_REQUESTED_ACTION_NOT_MERGE",action="MARK_READY_ONLY")

    def test_publication_requested_action_rejected(self):
        self.fail_with("DENY_REQUESTED_ACTION_NOT_MERGE",action="PRODUCTION_PUBLISH_ONLY")

    def test_invalid_phase_rejected(self):
        self.fail_with("DENY_UNKNOWN_MERGE_PHASE",phase="PUBLISH")

    def test_real_audience_holds(self):
        self.fail_with("HOLD_REAL_MERGE_VERIFIER_UNIMPLEMENTED",
                       policy=replace(self.f.policy,audience="PRODUCTION"))

    def test_unspecified_owner_registry_holds(self):
        r=evaluate_merge_only(self.f.envelope(),registry=None,policy=self.f.policy,
                              provider=self.f.provider,ledger=self.f.ledger,now_utc=NOW)
        self.assertEqual(r.code,"HOLD_INDEPENDENT_OWNER_REGISTRY_NOT_INSTALLED")

    def test_no_signer_id_holds(self):
        self.fail_with("DENY_SIGNER_OR_REPO_FORMAT",envelope=self.sign(issuer_key_id="bad"))

    def test_unknown_signer_denied(self):
        self.fail_with("DENY_UNKNOWN_SIGNER",envelope=self.sign(issuer_key_id="unknown-synthetic"))

    def test_revoked_signer_denied(self):
        self.fail_with("DENY_REVOKED_OWNER_KEY",registry=replace(
            self.f.registry,revoked_ids=frozenset({self.f.payload["issuer_key_id"]})))

    def test_owner_registry_version_drifts(self):
        self.fail_with("HOLD_OWNER_REGISTRY_VERSION_DRIFT",registry=replace(
            self.f.registry,version="other-registry"))

    def test_independent_merge_app_not_equal_existing_ci_app(self):
        self.fail_with("HOLD_MERGE_APP_NOT_INDEPENDENT",registry=replace(
            self.f.registry,independent_app_id=CI_APPS["static-release"]))

    def test_invalid_public_key_length_holds(self):
        self.fail_with("HOLD_PUBLIC_KEY_INVALID",registry=replace(
            self.f.registry,public_keys={self.f.payload["issuer_key_id"]:b"bad"}))

    def test_wrong_signature_denied(self):
        e=json.loads(self.f.envelope())
        e["signature_hex"]="0"*128
        self.fail_with("DENY_MERGE_SIGNATURE",envelope=canonical_bytes(e))

    def test_unknown_envelope_field_denied(self):
        e=json.loads(self.f.envelope())
        e["extra"]="self-approved"
        self.fail_with("DENY_ENVELOPE_FIELDS",envelope=canonical_bytes(e))

    def test_unknown_signed_payload_field_denied(self):
        self.fail_with("DENY_SIGNED_FIELDS",envelope=self.sign(
            new_admin_permission="superuser"))

    def test_invalid_signature_hex_denied(self):
        e=json.loads(self.f.envelope());e["signature_hex"]="F"*128
        self.fail_with("DENY_SIGNATURE_ENCODING",envelope=canonical_bytes(e))

    def test_non_string_repo_denied(self):
        self.fail_with("DENY_FIELD_TYPE_OR_ASCII",envelope=self.sign(repo=4))

    def test_non_ascii_signed_string_denied(self):
        self.fail_with("DENY_FIELD_TYPE_OR_ASCII",envelope=self.sign(base_branch="мейн"))

    def test_nonpositive_pr_denied(self):
        self.fail_with("DENY_PR_TYPE",envelope=self.sign(pr=0))

    def test_schema_downgrade_denied(self):
        self.fail_with("DENY_SCHEMA_OR_VERSION",envelope=self.sign(
            schema="ai-skill-lab.owner-admission.v1"))

    def test_policy_version_downgrade_denied(self):
        self.fail_with("DENY_SCHEMA_OR_VERSION",envelope=self.sign(policy_version="old"))

    def test_unexpected_merge_method_denied(self):
        self.fail_with("DENY_WRONG_ACTION_OR_METHOD",envelope=self.sign(merge_method="squash"))

    def test_merge_check_name_must_be_specific(self):
        self.fail_with("DENY_WRONG_ACTION_OR_METHOD",envelope=self.sign(
            required_merge_context="owner-admission"))

    def test_publisher_can_never_enable_auto_merge(self):
        eff={**PROHIBITED_EFFECTS,"auto_merge":True}
        self.fail_with("DENY_PROHIBITED_EFFECTS",envelope=self.sign(prohibited_effects=eff))

    def test_publisher_can_never_authorize_deploy(self):
        eff={**PROHIBITED_EFFECTS,"deploy":True}
        self.fail_with("DENY_PROHIBITED_EFFECTS",envelope=self.sign(prohibited_effects=eff))

    def test_publisher_cannot_authorize_mark_ready(self):
        eff={**PROHIBITED_EFFECTS,"mark_ready":True}
        self.fail_with("DENY_PROHIBITED_EFFECTS",envelope=self.sign(prohibited_effects=eff))

    def test_malformed_utc_denied(self):
        self.fail_with("DENY_UTC_FORMAT",envelope=self.sign(
            expires_at_utc="2026-10-12T13:10:00+00:00"))

    def test_signature_ttl_exceeded_denied(self):
        self.fail_with("DENY_MERGE_TTL",envelope=self.sign(
            expires_at_utc="2026-10-12T15:01:00Z"))

    def test_expired_at_exact_second_denied(self):
        self.fail_with("DENY_SIGNED_APPROVAL_EXPIRED",now=datetime(
            2026,10,12,13,10,tzinfo=timezone.utc))

    def test_green_check_does_not_extend_signature_ttl(self):
        provider=self.f.after_prepare()
        self.fail_with("DENY_SIGNED_APPROVAL_EXPIRED",phase="JIT_EXECUTION",
                       provider=provider,now=datetime(2026,10,12,13,10,tzinfo=timezone.utc))

    def test_clock_in_future_rejected(self):
        self.fail_with("DENY_FUTURE_ISSUANCE",now=datetime(
            2026,10,12,12,58,tzinfo=timezone.utc))

    def test_naive_now_holds(self):
        self.fail_with("HOLD_SYNTHETIC_UTC_CLOCK_INVALID",now=NOW.replace(tzinfo=None))

    def test_policy_expired_or_invalid_ttl_budget_holds(self):
        self.fail_with("HOLD_SYNTHETIC_TIMING_POLICY_INVALID",policy=replace(
            self.f.policy,max_ttl_seconds=0))

    def test_tampered_pr_id_stops(self):
        self.fail_with("STOP_MERGE_POLICY_TARGET_DRIFT",envelope=self.sign(pr=227))

    def test_tampered_base_branch_stops(self):
        self.fail_with("STOP_MERGE_POLICY_TARGET_DRIFT",envelope=self.sign(base_branch="dev"))

    def test_malicious_repo_name_denied(self):
        self.fail_with("DENY_SIGNER_OR_REPO_FORMAT",envelope=self.sign(repo="../../escape"))

    def test_tampered_base_sha_stops(self):
        self.fail_with("STOP_MERGE_SHA_OR_TREE_DRIFT",envelope=self.sign(base_commit="a"*40))

    def test_tampered_head_sha_stops(self):
        self.fail_with("STOP_MERGE_SHA_OR_TREE_DRIFT",envelope=self.sign(head_commit="b"*40))

    def test_tampered_tree_sha_stops(self):
        self.fail_with("STOP_MERGE_SHA_OR_TREE_DRIFT",envelope=self.sign(head_tree="c"*40))

    def test_tampered_patch_digest_denied(self):
        self.fail_with("DENY_MERGE_EVIDENCE_OR_PATCH_DRIFT",envelope=self.sign(patch_sha256="f"*64))

    def test_tampered_evidence_digest_denied(self):
        self.fail_with("DENY_MERGE_EVIDENCE_OR_PATCH_DRIFT",envelope=self.sign(evidence_sha256="f"*64))

    def test_tampered_paths_digest_denied(self):
        self.fail_with("DENY_MERGE_FILE_DIGEST",envelope=self.sign(allowed_paths_digest="f"*64))

    def test_extra_path_denied(self):
        snap=replace(self.f.provider,changed_paths=self.f.provider.changed_paths+(".env",))
        self.fail_with("DENY_MERGE_FILE_SCOPE",provider=snap)

    def test_path_traversal_denied(self):
        snap=replace(self.f.provider,changed_paths=("../.git/config",))
        self.fail_with("DENY_MERGE_FILE_SCOPE",provider=snap)

    def test_duplicate_path_denied(self):
        snap=replace(self.f.provider,changed_paths=self.f.provider.changed_paths+(PATHS[0],))
        self.fail_with("DENY_MERGE_FILE_SCOPE",provider=snap)

    def test_pr_still_draft_holds(self):
        self.fail_with("HOLD_MERGE_PR_NOT_READY_OR_MERGEABLE",provider=replace(
            self.f.provider,draft=True))

    def test_pr_not_mergeable_holds(self):
        self.fail_with("HOLD_MERGE_PR_NOT_READY_OR_MERGEABLE",provider=replace(
            self.f.provider,mergeable=False))

    def test_pr_closed_holds(self):
        self.fail_with("HOLD_MERGE_PR_NOT_READY_OR_MERGEABLE",provider=replace(
            self.f.provider,state="CLOSED"))

    def test_provider_snapshot_forged_source_holds(self):
        self.fail_with("HOLD_INDEPENDENT_PROVIDER_NOT_IMPLEMENTED",provider=replace(
            self.f.provider,source="GITHUB_VERIFIED_PRODUCTION"))

    def test_missing_provider_holds(self):
        r=evaluate_merge_only(self.f.envelope(),registry=self.f.registry,
                              policy=self.f.policy,provider=None,ledger=self.f.ledger,
                              now_utc=NOW)
        self.assertEqual(r.code,"HOLD_INDEPENDENT_PROVIDER_NOT_IMPLEMENTED")

    def test_provider_snapshot_stale_holds(self):
        self.fail_with("HOLD_PROVIDER_SNAPSHOT_NOT_JIT",provider=replace(
            self.f.provider,observed_at_utc="2026-10-12T12:58:00Z"))

    def test_provider_clock_noncanonical_holds(self):
        self.fail_with("HOLD_PROVIDER_CLOCK_INVALID",provider=replace(
            self.f.provider,observed_at_utc="2026-10-12T13:01:00+00:00"))

    def test_missing_main_protection_holds(self):
        rule=replace(self.f.provider.rule,protected=False)
        self.fail_with("HOLD_MERGE_BRANCH_RULE_NOT_ENFORCED",provider=replace(self.f.provider,rule=rule))

    def test_missing_provider_nonbypass_holds(self):
        rule=replace(self.f.provider.rule,no_bypass=False)
        self.fail_with("HOLD_MERGE_BRANCH_RULE_NOT_ENFORCED",provider=replace(self.f.provider,rule=rule))

    def test_force_pushes_enabled_holds(self):
        rule=replace(self.f.provider.rule,allow_force_pushes=True)
        self.fail_with("HOLD_MERGE_BRANCH_RULE_NOT_ENFORCED",provider=replace(self.f.provider,rule=rule))

    def test_linear_history_incompatible_holds(self):
        rule=replace(self.f.provider.rule,require_linear_history=True)
        self.fail_with("HOLD_MERGE_BRANCH_RULE_NOT_ENFORCED",provider=replace(self.f.provider,rule=rule))

    def test_missing_owner_merge_status_in_branch_rule_holds(self):
        rule=replace(self.f.provider.rule,required_check_app_ids=CI_APPS)
        self.fail_with("HOLD_MERGE_CONTEXT_NOT_REQUIRED_BY_PROVIDER",provider=replace(self.f.provider,rule=rule))

    def test_old_mark_ready_context_cannot_replace_merge_context(self):
        rule=replace(self.f.provider.rule,required_check_app_ids={**CI_APPS,"owner-admission":MERGE_APP})
        self.fail_with("HOLD_MERGE_CONTEXT_NOT_REQUIRED_BY_PROVIDER",provider=replace(self.f.provider,rule=rule))

    def test_owner_merge_context_wrong_app_holds(self):
        rule=replace(self.f.provider.rule,required_check_app_ids={**CI_APPS,MERGE_CONTEXT:CI_APPS["CodeQL"]})
        self.fail_with("HOLD_MERGE_CONTEXT_NOT_REQUIRED_BY_PROVIDER",provider=replace(self.f.provider,rule=rule))

    def test_current_duplicate_push_pr_checks_hold(self):
        extra=SyntheticCheck("static-release",CI_APPS["static-release"],HEAD,
                             "completed","success","push")
        bad=replace(self.f.provider,check_runs=self.f.provider.check_runs+(extra,))
        self.fail_with("HOLD_DUPLICATE_CHECK_NAMES",provider=bad)

    def test_missing_codeql_holds(self):
        snap=replace(self.f.provider,check_runs=self.f.provider.check_runs[:-1])
        self.fail_with("HOLD_REQUIRED_CI_NOT_PRESENT",provider=snap)

    def test_forged_codeql_app_denied(self):
        checks=list(self.f.provider.check_runs)
        checks[2]=replace(checks[2],app_id=CI_APPS["static-release"])
        self.fail_with("DENY_CI_CHECK_WRONG_APP_OR_HEAD",provider=replace(self.f.provider,check_runs=tuple(checks)))

    def test_ci_wrong_head_denied(self):
        checks=list(self.f.provider.check_runs)
        checks[0]=replace(checks[0],head_commit="a"*40)
        self.fail_with("DENY_CI_CHECK_WRONG_APP_OR_HEAD",provider=replace(self.f.provider,check_runs=tuple(checks)))

    def test_ci_neutral_is_not_success(self):
        checks=list(self.f.provider.check_runs)
        checks[0]=replace(checks[0],conclusion="neutral")
        self.fail_with("HOLD_CI_CHECK_NOT_SUCCESS",provider=replace(self.f.provider,check_runs=tuple(checks)))

    def test_ci_skipped_is_not_success(self):
        checks=list(self.f.provider.check_runs)
        checks[1]=replace(checks[1],conclusion="skipped")
        self.fail_with("HOLD_CI_CHECK_NOT_SUCCESS",provider=replace(self.f.provider,check_runs=tuple(checks)))

    def test_preview_canceled_holds(self):
        previews=list(self.f.provider.previews)
        previews[0]=replace(previews[0],state="CANCELED")
        self.fail_with("HOLD_MERGE_PREVIEW_NOT_READY",provider=replace(self.f.provider,previews=tuple(previews)))

    def test_preview_wrong_commit_holds(self):
        previews=list(self.f.provider.previews)
        previews[0]=replace(previews[0],git_commit=BASE)
        self.fail_with("HOLD_MERGE_PREVIEW_NOT_READY",provider=replace(self.f.provider,previews=tuple(previews)))

    def test_preview_missing_holds(self):
        self.fail_with("HOLD_REQUIRED_MERGE_PREVIEWS_MISSING",provider=replace(self.f.provider,previews=()))

    def test_preview_duplicate_holds(self):
        preview=self.f.provider.previews[0]
        self.fail_with("HOLD_REQUIRED_MERGE_PREVIEWS_MISSING",provider=replace(self.f.provider,previews=(preview,preview)))

    def test_lease_expired_holds(self):
        lease=replace(self.f.provider.lease,expires_at_utc="2026-10-12T13:00:00Z")
        self.fail_with("HOLD_MERGE_LEASE_NOT_EXACT",provider=replace(self.f.provider,lease=lease))

    def test_lease_wrong_ref_holds(self):
        lease=replace(self.f.provider.lease,coordination_ref_sha="a"*40)
        self.fail_with("HOLD_MERGE_LEASE_NOT_EXACT",provider=replace(self.f.provider,lease=lease))

    def test_lease_authorizes_mark_ready_not_merge_holds(self):
        lease=replace(self.f.provider.lease,authorized_action="MARK_READY_ONLY")
        self.fail_with("HOLD_MERGE_LEASE_NOT_EXACT",provider=replace(self.f.provider,lease=lease))

    def test_lease_clock_invalid_holds(self):
        lease=replace(self.f.provider.lease,expires_at_utc="not UTC")
        self.fail_with("HOLD_MERGE_LEASE_CLOCK_INVALID",provider=replace(self.f.provider,lease=lease))

    def test_reuse_same_nonce_denied(self):
        self.assertEqual(self.f.evaluate().status,"TEST_ONLY_PASS")
        self.fail_with("DENY_MERGE_NONCE_REPLAY")

    def test_absent_issuance_denied(self):
        import sqlite3
        with closing(sqlite3.connect(self.f.ledger_path)) as db, db:db.execute("DELETE FROM issued")
        self.fail_with("DENY_MERGE_NONCE_NOT_PREISSUED")

    def test_ledger_missing_holds(self):
        missing=SyntheticMergeLedger(os.path.join(self.f.dir.name,"nope.sqlite"),
                                     self.f.policy.ledger_id)
        self.fail_with("HOLD_MERGE_LEDGER_UNAVAILABLE",ledger=missing)

    def test_ledger_uninstalled_holds(self):
        r=evaluate_merge_only(self.f.envelope(),registry=self.f.registry,
                              policy=self.f.policy,provider=self.f.provider,
                              ledger=None,now_utc=NOW)
        self.assertEqual(r.code,"HOLD_INDEPENDENT_MERGE_LEDGER_UNIMPLEMENTED")

    def test_ledger_wrong_identity_holds(self):
        wrong=SyntheticMergeLedger(self.f.ledger_path,"bad-ledger")
        self.fail_with("HOLD_INDEPENDENT_MERGE_LEDGER_UNIMPLEMENTED",ledger=wrong)

    def test_preexisting_merge_check_holds_prepare(self):
        snap=replace(self.f.provider,check_runs=self.f.provider.check_runs+(self.f.check(),))
        self.fail_with("HOLD_MERGE_CHECK_ALREADY_EXISTS",provider=snap)

    def test_jit_missing_merge_check_holds(self):
        self.f.evaluate()
        snap=replace(self.f.provider,observed_at_utc="2026-10-12T13:02:00Z")
        self.fail_with("HOLD_REQUIRED_MERGE_CHECK_MISSING",phase="JIT_EXECUTION",provider=snap,now=JIT_NOW)

    def test_jit_wrong_app_check_denied(self):
        snap=self.f.after_prepare()
        checks=snap.check_runs[:-1]+(replace(snap.check_runs[-1],app_id=CI_APPS["CodeQL"]),)
        self.fail_with("DENY_MERGE_CHECK_SOURCE_OR_BINDING",phase="JIT_EXECUTION",now=JIT_NOW,
                       provider=replace(snap,check_runs=checks))

    def test_jit_owner_mark_ready_check_not_merge_holds(self):
        snap=self.f.after_prepare()
        bad=replace(snap.check_runs[-1],name="owner-admission")
        self.fail_with("HOLD_REQUIRED_MERGE_CHECK_MISSING",phase="JIT_EXECUTION",now=JIT_NOW,
                       provider=replace(snap,check_runs=snap.check_runs[:-1]+(bad,)))

    def test_jit_check_external_id_not_signed_denied(self):
        snap=self.f.after_prepare()
        bad=replace(snap.check_runs[-1],external_id="owner-merge-admission:wrong")
        self.fail_with("DENY_MERGE_CHECK_SOURCE_OR_BINDING",phase="JIT_EXECUTION",now=JIT_NOW,
                       provider=replace(snap,check_runs=snap.check_runs[:-1]+(bad,)))

    def test_jit_check_different_head_denied(self):
        snap=self.f.after_prepare()
        bad=replace(snap.check_runs[-1],head_commit=BASE)
        self.fail_with("DENY_MERGE_CHECK_SOURCE_OR_BINDING",phase="JIT_EXECUTION",now=JIT_NOW,
                       provider=replace(snap,check_runs=snap.check_runs[:-1]+(bad,)))

    def test_jit_neutral_owner_check_is_not_green(self):
        snap=self.f.after_prepare()
        bad=replace(snap.check_runs[-1],conclusion="neutral")
        self.fail_with("HOLD_MERGE_CHECK_NOT_SUCCESS",phase="JIT_EXECUTION",now=JIT_NOW,
                       provider=replace(snap,check_runs=snap.check_runs[:-1]+(bad,)))

    def test_jit_skipped_owner_check_is_not_green(self):
        snap=self.f.after_prepare()
        bad=replace(snap.check_runs[-1],conclusion="skipped")
        self.fail_with("HOLD_MERGE_CHECK_NOT_SUCCESS",phase="JIT_EXECUTION",now=JIT_NOW,
                       provider=replace(snap,check_runs=snap.check_runs[:-1]+(bad,)))

    def test_jit_check_from_future_holds(self):
        snap=self.f.after_prepare()
        bad=replace(snap.check_runs[-1],completed_at_utc="2026-10-12T14:01:30Z")
        self.fail_with("HOLD_MERGE_CHECK_TIME_DRIFT",phase="JIT_EXECUTION",now=JIT_NOW,
                       provider=replace(snap,check_runs=snap.check_runs[:-1]+(bad,)))

    def test_jit_noncanonical_merge_check_time_holds(self):
        snap=self.f.after_prepare()
        bad=replace(snap.check_runs[-1],completed_at_utc="invalid timestamp")
        self.fail_with("HOLD_MERGE_CHECK_TIME_INVALID",phase="JIT_EXECUTION",now=JIT_NOW,
                       provider=replace(snap,check_runs=snap.check_runs[:-1]+(bad,)))

    def test_malformed_branch_required_check_mapping_denied(self):
        rule=replace(self.f.provider.rule,required_check_app_ids=None)
        self.fail_with("DENY_SYNTHETIC_MERGE_CONTRACT_INVALID",
                       provider=replace(self.f.provider,rule=rule))

    def test_jit_duplicate_merge_check_holds(self):
        snap=self.f.after_prepare()
        self.fail_with("HOLD_DUPLICATE_CHECK_NAMES",phase="JIT_EXECUTION",now=JIT_NOW,
                       provider=replace(snap,check_runs=snap.check_runs+(snap.check_runs[-1],)))

    def test_jit_unsigned_new_commit_stops(self):
        snap=self.f.after_prepare()
        self.fail_with("STOP_MERGE_SHA_OR_TREE_DRIFT",phase="JIT_EXECUTION",now=JIT_NOW,
                       provider=replace(snap,head_commit="9"*40))

    def test_jit_new_branch_rules_holds(self):
        snap=self.f.after_prepare()
        rule=replace(snap.rule,no_bypass=False)
        self.fail_with("HOLD_MERGE_BRANCH_RULE_NOT_ENFORCED",phase="JIT_EXECUTION",now=JIT_NOW,
                       provider=replace(snap,rule=rule))

    def test_jit_owner_key_revoked_holds(self):
        snap=self.f.after_prepare()
        reg=replace(self.f.registry,revoked_ids=frozenset({self.f.payload["issuer_key_id"]}))
        self.fail_with("DENY_REVOKED_OWNER_KEY",phase="JIT_EXECUTION",now=JIT_NOW,
                       provider=snap,registry=reg)

    def test_jit_provider_stale_holds(self):
        snap=self.f.after_prepare()
        self.fail_with("HOLD_PROVIDER_SNAPSHOT_NOT_JIT",phase="JIT_EXECUTION",now=datetime(
            2026,10,12,13,7,tzinfo=timezone.utc),provider=snap)

    def test_jit_ledger_consumption_lost_holds(self):
        import sqlite3
        snap=self.f.after_prepare()
        with closing(sqlite3.connect(self.f.ledger_path)) as db, db:db.execute("DELETE FROM consumed")
        self.fail_with("HOLD_MERGE_NONCE_CONSUMPTION_NOT_VERIFIED",phase="JIT_EXECUTION",now=JIT_NOW,
                       provider=snap)

    def test_jit_correct_app_but_expired_lease_holds(self):
        snap=self.f.after_prepare()
        lease=replace(snap.lease,expires_at_utc="2026-10-12T13:01:30Z")
        self.fail_with("HOLD_MERGE_LEASE_NOT_EXACT",phase="JIT_EXECUTION",now=JIT_NOW,
                       provider=replace(snap,lease=lease))

    def test_jit_no_real_execution_even_with_green_check(self):
        snap=self.f.after_prepare()
        r=self.f.evaluate(phase="JIT_EXECUTION",now=JIT_NOW,provider=snap)
        self.assertEqual(r.status,"TEST_ONLY_PASS")
        self.assertFalse(r.merge_authorized)
        self.assertFalse(r.execution_action_performed)
        self.assertFalse(r.github_check_publishable)


if __name__=="__main__":
    unittest.main()
