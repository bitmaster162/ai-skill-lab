"""Offline deterministic attestation verifier. NO production authority.

Checks are a *test contract*, not live GitHub attestations: snapshots are
synthetic inputs. In particular, an untrusted caller could fabricate them.
No network, check-run creation, real-key issuance, GitHub settings, or deploy.
A future separately-controlled verifier must supply authenticated provider
facts, owner key custody, CAS ledger service and source-pinned status publisher.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .canonical import (
    DOMAIN, InvalidDocument, canonical_bytes, canonical_sha256,
    sha256_bytes, strict_json_bytes, utc_timestamp,
)
from .contracts import ProviderSnapshot, TestPolicy, TrustRegistry
from .ledger import NonceLedgerError, NonceNotIssued, NonceReplayed, SqliteNonceLedger

HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
HEX128 = re.compile(r"[0-9a-f]{128}\Z")
KEY_ID = re.compile(r"[a-z0-9][a-z0-9_-]{3,63}\Z")
REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
SCHEMA = "ai-skill-lab.owner-admission.v1"
POLICY_VERSION = "R4F7F_OFFLINE_CONTRACT_R1"
RECEIPT_SCHEMA = "ai-skill-lab.r4f7f.offline-evaluation.v1"
ACTION = "MARK_READY_ONLY"
REVIEW_MODE = "SOURCE_ONLY_NO_RELEASE"
LIMITS = {"merge": False, "production_publish": False,
          "force_push": False, "deploy": False}
REQUIRED_FIELDS = frozenset({
    "schema", "policy_version", "issuer_key_id", "repo", "pr", "action",
    "base_commit", "base_tree", "head_commit", "head_tree",
    "evidence_sha256", "allowed_paths_digest", "patch_sha256",
    "issued_at_utc", "expires_at_utc", "nonce", "review_mode",
    "coordination_ref_sha", "limits",
})


class GateFailure(Exception):
    def __init__(self, status: str, code: str):
        super().__init__(code)
        self.status, self.code = status, code


def _gate(condition: bool, status: str, code: str) -> None:
    if condition is not True:
        raise GateFailure(status, code)


def _eq_type(obj: Any, expected: type) -> bool:
    return type(obj) is expected


def _sha40(value: Any) -> bool:
    return _eq_type(value, str) and bool(HEX40.fullmatch(value))


def _sha64(value: Any) -> bool:
    return _eq_type(value, str) and bool(HEX64.fullmatch(value))


def _valid_path(path: Any) -> bool:
    return (type(path) is str and 1 <= len(path) <= 260 and
            path.isascii() and path[0] != "/" and "\\" not in path and
            not any(c in path for c in "\x00\r\n") and
            all(part not in ("", ".", "..") for part in path.split("/")))


@dataclass(frozen=True)
class EvaluationReceipt:
    status: str
    code: str
    test_only: bool = True
    eligible_for_real_action: bool = False
    merge_authorized: bool = False
    production_publish_authorized: bool = False
    github_check_publishable: bool = False
    nonce_consumed: bool = False
    payload_sha256: str | None = None
    signer_public_fingerprint_sha256: str | None = None

    def as_dict(self) -> dict:
        return {"schema": RECEIPT_SCHEMA, "status": self.status,
                "code": self.code, "test_only": self.test_only,
                "eligible_for_real_action": self.eligible_for_real_action,
                "merge_authorized": self.merge_authorized,
                "production_publish_authorized": self.production_publish_authorized,
                "github_check_publishable": self.github_check_publishable,
                "nonce_consumed": self.nonce_consumed,
                "payload_sha256": self.payload_sha256,
                "signer_public_fingerprint_sha256": self.signer_public_fingerprint_sha256}


def _validate_structure(envelope: dict) -> dict:
    _gate(set(envelope) == {"payload", "signature_hex"}, "DENY", "DENY_ENVELOPE_FIELDS")
    p = envelope.get("payload")
    sig = envelope.get("signature_hex")
    _gate(type(p) is dict and set(p) == REQUIRED_FIELDS, "DENY", "DENY_PAYLOAD_FIELDS")
    _gate(type(sig) is str and bool(HEX128.fullmatch(sig)), "DENY", "DENY_SIGNATURE_ENCODING")
    string_fields = REQUIRED_FIELDS - {"pr", "limits"}
    _gate(all(type(p[f]) is str and p[f].isascii() and len(p[f]) <= 256
              for f in string_fields), "DENY", "DENY_FIELD_TYPE_OR_ASCII")
    _gate(type(p["pr"]) is int and p["pr"] > 0, "DENY", "DENY_PR_TYPE")
    _gate(type(p["limits"]) is dict and set(p["limits"]) == set(LIMITS) and
          all(type(v) is bool for v in p["limits"].values()), "DENY", "DENY_LIMITS_SCHEMA")
    _gate(p["schema"] == SCHEMA and p["policy_version"] == POLICY_VERSION,
          "DENY", "DENY_SCHEMA_OR_POLICY_VERSION")
    _gate(p["action"] == ACTION and p["review_mode"] == REVIEW_MODE,
          "DENY", "DENY_UNSUPPORTED_ACTION_OR_REVIEW_MODE")
    _gate(p["limits"] == LIMITS, "DENY", "DENY_NONZERO_EFFECT_SCOPE")
    _gate(bool(KEY_ID.fullmatch(p["issuer_key_id"])), "DENY", "DENY_KEY_ID_FORMAT")
    _gate(bool(REPO.fullmatch(p["repo"])), "DENY", "DENY_REPO_FORMAT")
    for key in ("base_commit", "base_tree", "head_commit", "head_tree", "coordination_ref_sha"):
        _gate(_sha40(p[key]), "DENY", "DENY_COMMIT_OR_TREE_FORMAT")
    for key in ("evidence_sha256", "allowed_paths_digest", "patch_sha256"):
        _gate(_sha64(p[key]), "DENY", "DENY_DIGEST_FORMAT")
    _gate(bool(re.fullmatch(r"[0-9a-f]{32}", p["nonce"])), "DENY", "DENY_NONCE_FORMAT")
    for key in ("issued_at_utc", "expires_at_utc"):
        try:
            utc_timestamp(p[key])
        except InvalidDocument as exc:
            raise GateFailure("DENY", "DENY_TIMESTAMP_FORMAT") from exc
    return p


def _validate_root(p: dict, sig: str, registry: TrustRegistry | None) -> str:
    _gate(type(registry) is TrustRegistry and bool(registry.registry_version) and
          bool(registry.owner_public_keys) and type(registry.independent_app_id) is int and
          registry.independent_app_id > 0, "HOLD", "HOLD_EXTERNAL_ROOT_NOT_INSTALLED")
    kid = p["issuer_key_id"]
    _gate(kid not in registry.revoked_owner_key_ids, "DENY", "DENY_REVOKED_OWNER_KEY")
    _gate(kid in registry.owner_public_keys, "DENY", "DENY_OWNER_KEY_NOT_PINNED")
    pub = registry.owner_public_keys[kid]
    _gate(type(pub) is bytes and len(pub) == 32, "HOLD", "HOLD_OWNER_PUBLIC_KEY_INVALID")
    try:
        Ed25519PublicKey.from_public_bytes(pub).verify(
            bytes.fromhex(sig), DOMAIN + canonical_bytes(p))
    except (InvalidSignature, ValueError) as exc:
        raise GateFailure("DENY", "DENY_ED25519_SIGNATURE") from exc
    return sha256_bytes(pub)


def _validate_time(p: dict, policy: TestPolicy, now: datetime) -> None:
    _gate(type(now) is datetime and now.tzinfo is not None and now.utcoffset().total_seconds() == 0,
          "HOLD", "HOLD_UTC_CLOCK_REQUIRED")
    _gate(type(policy.max_ttl_seconds) is int and 0 < policy.max_ttl_seconds and
          type(policy.max_future_skew_seconds) is int and 0 <= policy.max_future_skew_seconds and
          type(policy.max_provider_age_seconds) is int and policy.max_provider_age_seconds > 0,
          "HOLD", "HOLD_INVALID_OWNER_POLICY_BUDGET")
    issued = utc_timestamp(p["issued_at_utc"])
    expiry = utc_timestamp(p["expires_at_utc"])
    _gate(0 < (expiry - issued).total_seconds() <= policy.max_ttl_seconds,
          "DENY", "DENY_ATTESTATION_TTL")
    _gate((issued - now).total_seconds() <= policy.max_future_skew_seconds,
          "DENY", "DENY_ISSUED_IN_FUTURE")
    _gate(now < expiry, "DENY", "DENY_ATTESTATION_EXPIRED")


def _validate_provider(p: dict, policy: TestPolicy, registry: TrustRegistry,
                       snap: ProviderSnapshot | None, now: datetime) -> None:
    _gate(type(snap) is ProviderSnapshot, "HOLD", "HOLD_PROVIDER_SNAPSHOT_UNAVAILABLE")
    _gate(type(snap.observed_at_utc) is str, "HOLD", "HOLD_PROVIDER_TIME_UNKNOWN")
    try:
        observed = utc_timestamp(snap.observed_at_utc)
    except InvalidDocument as exc:
        raise GateFailure("HOLD", "HOLD_PROVIDER_TIMESTAMP_BAD") from exc
    _gate((observed - now).total_seconds() <= policy.max_future_skew_seconds and
          0 <= (now - observed).total_seconds() <= policy.max_provider_age_seconds,
          "HOLD", "HOLD_PROVIDER_SNAPSHOT_STALE")
    _gate(snap.repo == policy.repo == p["repo"] and snap.pr == policy.pr == p["pr"],
          "STOP", "STOP_REPO_OR_PR_DRIFT")
    _gate(snap.state == "OPEN" and snap.draft is True,
          "HOLD", "HOLD_PR_NOT_OPEN_DRAFT")
    for f in ("base_commit", "base_tree", "head_commit", "head_tree"):
        _gate(_sha40(getattr(snap, f)) and getattr(snap, f) == p[f],
              "STOP", "STOP_SHA_OR_TREE_DRIFT")
    _gate(type(snap.changed_paths) is tuple and
          all(_valid_path(x) for x in snap.changed_paths) and
          len(snap.changed_paths) == len(set(snap.changed_paths)),
          "DENY", "DENY_CHANGED_PATH_INVENTORY")
    _gate(tuple(sorted(snap.changed_paths)) == tuple(sorted(policy.allowed_paths)),
          "DENY", "DENY_CHANGED_PATH_SCOPE")
    _gate(p["allowed_paths_digest"] == canonical_sha256(sorted(snap.changed_paths)),
          "DENY", "DENY_CHANGED_PATH_DIGEST")
    _gate(type(snap.raw_patch) is bytes and 0 < len(snap.raw_patch) <= policy.max_patch_bytes and
          sha256_bytes(snap.raw_patch) == p["patch_sha256"],
          "DENY", "DENY_PATCH_SHA256_DRIFT")
    _gate(type(snap.raw_evidence) is bytes and 0 < len(snap.raw_evidence) <= policy.max_evidence_bytes and
          sha256_bytes(snap.raw_evidence) == p["evidence_sha256"],
          "DENY", "DENY_EVIDENCE_SHA256_DRIFT")

    rule = snap.rule
    _gate(rule.protected is True and rule.require_pull_request is True and
          rule.require_status_checks is True and rule.require_branch_up_to_date is True and
          rule.require_conversation_resolution is True and rule.no_bypass is True and
          rule.allow_force_pushes is False and rule.allow_deletions is False,
          "HOLD", "HOLD_PROVIDER_PROTECTION_INSUFFICIENT")
    _gate(rule.require_linear_history is False, "HOLD", "HOLD_NORMAL_MERGE_INCOMPATIBLE_RULE")
    _gate(registry.independent_app_id not in set(policy.required_ci_app_ids.values()),
          "HOLD", "HOLD_OWNER_APP_NOT_INDEPENDENT")
    expected_checks = dict(policy.required_ci_app_ids)
    expected_checks["owner-admission"] = registry.independent_app_id
    _gate(dict(rule.required_check_app_ids) == expected_checks,
          "HOLD", "HOLD_TRUSTED_OWNER_STATUS_NOT_REQUIRED")

    _gate(type(snap.check_runs) is tuple, "HOLD", "HOLD_CI_SNAPSHOT_INVALID")
    required = set(policy.required_ci_app_ids)
    relevant = [c for c in snap.check_runs if c.name in required]
    names = [c.name for c in relevant]
    _gate(len(names) == len(set(names)), "HOLD", "HOLD_DUPLICATE_CHECK_NAME_AMBIGUITY")
    _gate(set(names) == required, "HOLD", "HOLD_REQUIRED_CI_MISSING")
    for check in relevant:
        _gate(type(check.app_id) is int and check.app_id == policy.required_ci_app_ids[check.name] and
              check.head_commit == p["head_commit"] and check.event == "pull_request",
              "DENY", "DENY_CI_WRONG_APP_HEAD_OR_EVENT")
        _gate(check.status == "completed" and check.conclusion == "success",
              "HOLD", "HOLD_CI_NOT_SUCCESS")

    _gate(type(snap.previews) is tuple, "HOLD", "HOLD_PREVIEW_LIST_MISSING")
    _gate(len(snap.previews) == len(set(v.project_id for v in snap.previews)),
          "HOLD", "HOLD_DUPLICATE_PREVIEW_PROJECT")
    _gate(set(v.project_id for v in snap.previews) == set(policy.preview_project_ids),
          "HOLD", "HOLD_REQUIRED_PREVIEW_MISSING")
    for preview in snap.previews:
        _gate(preview.state == "READY" and preview.git_commit == p["head_commit"],
              "HOLD", "HOLD_REQUIRED_PREVIEW_NOT_READY")

    lease = snap.lease
    try:
        lease_expiry = utc_timestamp(lease.expires_at_utc)
    except InvalidDocument as exc:
        raise GateFailure("HOLD", "HOLD_LEASE_EXPIRY_INVALID") from exc
    _gate(lease_expiry > now and lease.conflict_free is True and
          lease.target_repo == p["repo"] and lease.target_head_commit == p["head_commit"] and
          lease.coordination_ref_sha == p["coordination_ref_sha"] and
          lease.authorized_action == ACTION,
          "HOLD", "HOLD_COORDINATION_LEASE_NOT_AUTHORIZED")


def evaluate(envelope_bytes: bytes, *, registry: TrustRegistry | None,
             policy: TestPolicy, provider: ProviderSnapshot | None,
             ledger: SqliteNonceLedger | None, now_utc: datetime,
             requested_action: str = ACTION) -> EvaluationReceipt:
    """Pure off-line admission checks + atomic TEST nonce consumption.

    This function never returns a real action grant, even on successful tests.
    Evidence caller-supplied and unauthenticated; App/source/ledger must still be
    built in an independent trust domain before any real deployment.
    """
    payload_sha: str | None = None
    fingerprint: str | None = None
    try:
        _gate(type(policy) is TestPolicy and policy.audience == "OFFLINE_TEST_ONLY",
              "HOLD", "HOLD_PRODUCTION_VERIFIER_UNIMPLEMENTED")
        _gate(policy.policy_version == POLICY_VERSION and policy.approved_action == ACTION and
              policy.review_mode == REVIEW_MODE and type(policy.repo) is str and
              type(policy.pr) is int and policy.pr > 0,
              "HOLD", "HOLD_TEST_POLICY_NOT_APPROVED")
        _gate(type(policy.allowed_paths) is tuple and len(policy.allowed_paths) > 0 and
              len(policy.allowed_paths) == len(set(policy.allowed_paths)) and
              all(_valid_path(p) for p in policy.allowed_paths) and
              type(policy.preview_project_ids) is tuple and len(policy.preview_project_ids) == 2 and
              len(set(policy.preview_project_ids)) == 2 and
              type(policy.max_patch_bytes) is int and policy.max_patch_bytes > 0 and
              type(policy.max_evidence_bytes) is int and policy.max_evidence_bytes > 0 and
              set(policy.required_ci_app_ids) == {"static-release", "language-parity", "CodeQL"} and
              all(type(a) is int and a > 0 for a in policy.required_ci_app_ids.values()),
              "HOLD", "HOLD_TEST_POLICY_BAD_SCOPE")
        _gate(type(requested_action) is str and requested_action == ACTION,
              "DENY", "DENY_ACTION_NOT_IN_OFFLINE_SCOPE")
        try:
            envelope = strict_json_bytes(envelope_bytes)
        except InvalidDocument as exc:
            raise GateFailure("DENY", "DENY_MALFORMED_ENVELOPE") from exc
        p = _validate_structure(envelope)
        payload_sha = canonical_sha256(p)
        _gate(p["repo"] == policy.repo and p["pr"] == policy.pr,
              "STOP", "STOP_POLICY_TARGET_MISMATCH")
        _gate(p["action"] == requested_action, "DENY", "DENY_ACTION_NOT_SIGNED")
        fingerprint = _validate_root(p, envelope["signature_hex"], registry)
        _validate_time(p, policy, now_utc)
        _validate_provider(p, policy, registry, provider, now_utc)
        _gate(type(ledger) is SqliteNonceLedger,
              "HOLD", "HOLD_INDEPENDENT_LEDGER_NOT_INSTALLED")
        try:
            ledger.consume(issuer_key_id=p["issuer_key_id"], nonce=p["nonce"],
                           payload_sha256=payload_sha, action=requested_action,
                           head_commit=p["head_commit"], expires_at_utc=p["expires_at_utc"],
                           consumed_at=now_utc)
        except NonceReplayed as exc:
            raise GateFailure("DENY", "DENY_REPLAYED_NONCE") from exc
        except NonceNotIssued as exc:
            raise GateFailure("DENY", "DENY_NONCE_NOT_IN_PREISSUED_LEDGER") from exc
        except NonceLedgerError as exc:
            raise GateFailure("HOLD", "HOLD_INDEPENDENT_LEDGER_UNAVAILABLE") from exc
        return EvaluationReceipt("TEST_ONLY_PASS", "PASS_OFFLINE_CONTRACT_ONLY",
                                 nonce_consumed=True, payload_sha256=payload_sha,
                                 signer_public_fingerprint_sha256=fingerprint)
    except GateFailure as exc:
        return EvaluationReceipt(exc.status, exc.code, payload_sha256=payload_sha,
                                 signer_public_fingerprint_sha256=fingerprint)
    except (InvalidDocument, AttributeError, TypeError, ValueError, OverflowError) as exc:
        # No raw exception contents in receipt: no secrets or injected status names.
        return EvaluationReceipt("DENY", "DENY_INVALID_CONTRACT",
                                 payload_sha256=payload_sha,
                                 signer_public_fingerprint_sha256=fingerprint)
