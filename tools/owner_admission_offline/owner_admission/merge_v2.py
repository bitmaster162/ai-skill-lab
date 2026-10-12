"""R4F7H: test-only MERGE_ONLY check preparation and pre-merge JIT validation.

No provider API, owner key, App credential, check publisher, or merge executor.
Input snapshots and clocks are synthetic and can be forged by the caller.
A successful result can NEVER authorize an actual GitHub action.
R4F7F MARK_READY_ONLY remains a separate, unchanged protocol.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .canonical import (
    InvalidDocument, canonical_bytes, canonical_sha256, sha256_bytes,
    strict_json_bytes, utc_timestamp,
)
from .merge_v2_contracts import (
    SyntheticMergePolicy, SyntheticOwnerRegistry, SyntheticProviderSnapshot,
    SyntheticCheck, SyntheticBranchRule, SyntheticLease, SyntheticPreview,
)
from .merge_v2_ledger import (
    MergeLedgerError, MergeNonceNotIssued, MergeNonceReplayed,
    SyntheticMergeLedger,
)

# Deliberately incompatible with R4F7F v1 domain and action.
DOMAIN = b"AI_SKILL_LAB_OWNER_MERGE_V2\x00"
SCHEMA = "ai-skill-lab.owner-merge-admission.v2"
POLICY_VERSION = "R4F7H_OFFLINE_MERGE_CONTRACT_R1"
RECEIPT_SCHEMA = "ai-skill-lab.r4f7h.offline-merge-evaluation.v1"
ACTION = "MERGE_ONLY"
MERGE_CONTEXT = "owner-merge-admission"
REVIEW_MODE = "SOURCE_ONLY_NO_RELEASE"
MERGE_METHOD = "merge"
SYNTHETIC_SOURCE = "SYNTHETIC_OFFLINE_FIXTURE"
PROHIBITED_EFFECTS = {
    "mark_ready": False,
    "production_publish": False,
    "deploy": False,
    "force_push": False,
    "branch_delete": False,
    "auto_merge": False,
    "squash": False,
    "rebase": False,
}
REQ = frozenset({
    "schema", "policy_version", "owner_registry_version", "issuer_key_id",
    "repo", "pr", "base_branch", "merge_method", "action",
    "base_commit", "base_tree", "head_commit", "head_tree",
    "patch_sha256", "evidence_sha256", "allowed_paths_digest",
    "coordination_ref_sha", "issued_at_utc", "expires_at_utc", "nonce",
    "review_mode", "required_merge_context", "prohibited_effects",
})
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
HEX128 = re.compile(r"[0-9a-f]{128}\Z")
NONCE = re.compile(r"[0-9a-f]{32}\Z")
KEY_ID = re.compile(r"[a-z0-9][a-z0-9_-]{3,63}\Z")
REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")


class GateFailure(Exception):
    def __init__(self, status: str, code: str):
        super().__init__(code)
        self.status = status
        self.code = code


def need(ok: bool, status: str, code: str) -> None:
    if ok is not True:
        raise GateFailure(status, code)


def sha40(v: Any) -> bool:
    return type(v) is str and bool(HEX40.fullmatch(v))


def sha64(v: Any) -> bool:
    return type(v) is str and bool(HEX64.fullmatch(v))


def valid_path(s: Any) -> bool:
    return (type(s) is str and 1 <= len(s) <= 260 and s.isascii() and
            s[0] != "/" and "\\" not in s and
            all(part not in ("", ".", "..") for part in s.split("/")) and
            not any(c in s for c in "\x00\r\n"))


@dataclass(frozen=True)
class MergeTestReceipt:
    status: str
    code: str
    phase: str
    test_only: bool = True
    real_owner_authority: bool = False
    github_check_publishable: bool = False
    merge_authorized: bool = False
    mark_ready_authorized: bool = False
    deploy_authorized: bool = False
    production_publish_authorized: bool = False
    nonce_consumed: bool = False
    payload_sha256: str | None = None
    owner_public_fingerprint_sha256: str | None = None
    independently_authenticated_provider: bool = False
    execution_action_performed: bool = False

    def as_dict(self) -> dict:
        return {"schema": RECEIPT_SCHEMA, **vars(self)}


def _payload(env: dict) -> dict:
    need(set(env) == {"payload", "signature_hex"}, "DENY", "DENY_ENVELOPE_FIELDS")
    p = env["payload"]
    sig = env["signature_hex"]
    need(type(p) is dict and set(p) == REQ, "DENY", "DENY_SIGNED_FIELDS")
    need(type(sig) is str and bool(HEX128.fullmatch(sig)),
         "DENY", "DENY_SIGNATURE_ENCODING")
    strings = REQ - {"pr", "prohibited_effects"}
    need(all(type(p[k]) is str and p[k].isascii() and len(p[k]) <= 256
             for k in strings), "DENY", "DENY_FIELD_TYPE_OR_ASCII")
    need(type(p["pr"]) is int and p["pr"] > 0, "DENY", "DENY_PR_TYPE")
    need(type(p["prohibited_effects"]) is dict and
         p["prohibited_effects"] == PROHIBITED_EFFECTS and
         all(type(v) is bool for v in p["prohibited_effects"].values()),
         "DENY", "DENY_PROHIBITED_EFFECTS")
    need(p["schema"] == SCHEMA and p["policy_version"] == POLICY_VERSION,
         "DENY", "DENY_SCHEMA_OR_VERSION")
    need(p["action"] == ACTION and p["merge_method"] == MERGE_METHOD and
         p["required_merge_context"] == MERGE_CONTEXT and
         p["review_mode"] == REVIEW_MODE, "DENY", "DENY_WRONG_ACTION_OR_METHOD")
    need(bool(KEY_ID.fullmatch(p["issuer_key_id"])) and
         bool(REPO.fullmatch(p["repo"])), "DENY", "DENY_SIGNER_OR_REPO_FORMAT")
    for k in ("base_commit", "base_tree", "head_commit", "head_tree", "coordination_ref_sha"):
        need(sha40(p[k]), "DENY", "DENY_GIT_SHA_FORMAT")
    for k in ("patch_sha256", "evidence_sha256", "allowed_paths_digest"):
        need(sha64(p[k]), "DENY", "DENY_CONTENT_DIGEST_FORMAT")
    need(bool(NONCE.fullmatch(p["nonce"])), "DENY", "DENY_NONCE_FORMAT")
    for k in ("issued_at_utc", "expires_at_utc"):
        try:
            utc_timestamp(p[k])
        except InvalidDocument as exc:
            raise GateFailure("DENY", "DENY_UTC_FORMAT") from exc
    return p


def _registry(p: dict, env: dict, registry: SyntheticOwnerRegistry | None,
              ci_apps: dict[str, int]) -> str:
    need(type(registry) is SyntheticOwnerRegistry and type(registry.version) is str
         and bool(registry.version) and type(registry.independent_app_id) is int
         and registry.independent_app_id > 0 and bool(registry.public_keys),
         "HOLD", "HOLD_INDEPENDENT_OWNER_REGISTRY_NOT_INSTALLED")
    need(p["owner_registry_version"] == registry.version,
         "HOLD", "HOLD_OWNER_REGISTRY_VERSION_DRIFT")
    need(registry.independent_app_id not in set(ci_apps.values()),
         "HOLD", "HOLD_MERGE_APP_NOT_INDEPENDENT")
    kid = p["issuer_key_id"]
    need(kid not in registry.revoked_ids, "DENY", "DENY_REVOKED_OWNER_KEY")
    need(kid in registry.public_keys, "DENY", "DENY_UNKNOWN_SIGNER")
    pub = registry.public_keys[kid]
    need(type(pub) is bytes and len(pub) == 32, "HOLD", "HOLD_PUBLIC_KEY_INVALID")
    try:
        Ed25519PublicKey.from_public_bytes(pub).verify(
            bytes.fromhex(env["signature_hex"]), DOMAIN + canonical_bytes(p))
    except (InvalidSignature, ValueError) as exc:
        raise GateFailure("DENY", "DENY_MERGE_SIGNATURE") from exc
    return sha256_bytes(pub)


def _time(p: dict, policy: SyntheticMergePolicy, now: datetime) -> None:
    need(type(now) is datetime and now.tzinfo is not None and
         now.utcoffset() is not None and now.utcoffset().total_seconds() == 0,
         "HOLD", "HOLD_SYNTHETIC_UTC_CLOCK_INVALID")
    values = (policy.max_ttl_seconds, policy.max_future_skew_seconds,
              policy.max_provider_age_seconds)
    need(all(type(x) is int for x in values) and
         policy.max_ttl_seconds > 0 and policy.max_future_skew_seconds >= 0 and
         policy.max_provider_age_seconds > 0,
         "HOLD", "HOLD_SYNTHETIC_TIMING_POLICY_INVALID")
    issue = utc_timestamp(p["issued_at_utc"])
    expires = utc_timestamp(p["expires_at_utc"])
    need(0 < (expires - issue).total_seconds() <= policy.max_ttl_seconds,
         "DENY", "DENY_MERGE_TTL")
    need((issue - now).total_seconds() <= policy.max_future_skew_seconds,
         "DENY", "DENY_FUTURE_ISSUANCE")
    need(now < expires, "DENY", "DENY_SIGNED_APPROVAL_EXPIRED")


def _policy(policy: SyntheticMergePolicy, action: str) -> None:
    need(type(policy) is SyntheticMergePolicy and
         policy.audience == "OFFLINE_TEST_ONLY", "HOLD", "HOLD_REAL_MERGE_VERIFIER_UNIMPLEMENTED")
    need(policy.policy_version == POLICY_VERSION and policy.action == ACTION and
         policy.merge_method == MERGE_METHOD and type(policy.repo) is str and
         type(policy.pr) is int and policy.pr > 0 and
         type(policy.base_branch) is str and policy.base_branch == "main" and
         type(policy.expected_require_approvals) is bool and
         type(policy.ledger_id) is str and bool(policy.ledger_id),
         "HOLD", "HOLD_SYNTHETIC_POLICY_INCOMPATIBLE")
    need(type(policy.allowed_paths) is tuple and bool(policy.allowed_paths) and
         len(set(policy.allowed_paths)) == len(policy.allowed_paths) and
         all(valid_path(s) for s in policy.allowed_paths) and
         type(policy.preview_projects) is tuple and
         len(policy.preview_projects) == len(set(policy.preview_projects)) == 2 and
         all(type(x) is str and bool(x) for x in policy.preview_projects) and
         type(policy.max_patch_bytes) is int and 0 < policy.max_patch_bytes and
         type(policy.max_evidence_bytes) is int and 0 < policy.max_evidence_bytes and
         dict(policy.required_ci_apps).keys() == {"static-release", "language-parity", "CodeQL"} and
         all(type(x) is int and x > 0 for x in policy.required_ci_apps.values()),
         "HOLD", "HOLD_SYNTHETIC_POLICY_BAD_SCOPE")
    need(type(action) is str and action == ACTION, "DENY", "DENY_REQUESTED_ACTION_NOT_MERGE")


def _provider(p: dict, policy: SyntheticMergePolicy, registry: SyntheticOwnerRegistry,
              snap: SyntheticProviderSnapshot | None, now: datetime,
              phase: str, payload_sha: str) -> None:
    need(type(snap) is SyntheticProviderSnapshot and snap.source == SYNTHETIC_SOURCE,
         "HOLD", "HOLD_INDEPENDENT_PROVIDER_NOT_IMPLEMENTED")
    try:
        observed = utc_timestamp(snap.observed_at_utc)
    except InvalidDocument as exc:
        raise GateFailure("HOLD", "HOLD_PROVIDER_CLOCK_INVALID") from exc
    need((observed - now).total_seconds() <= policy.max_future_skew_seconds and
         0 <= (now - observed).total_seconds() <= policy.max_provider_age_seconds,
         "HOLD", "HOLD_PROVIDER_SNAPSHOT_NOT_JIT")
    need(snap.repo == policy.repo == p["repo"] and
         snap.pr == policy.pr == p["pr"] and
         snap.branch == policy.base_branch == p["base_branch"],
         "STOP", "STOP_MERGE_TARGET_CHANGED")
    need(snap.state == "OPEN" and snap.draft is False and snap.mergeable is True,
         "HOLD", "HOLD_MERGE_PR_NOT_READY_OR_MERGEABLE")
    for key in ("base_commit", "base_tree", "head_commit", "head_tree"):
        need(sha40(getattr(snap, key)) and getattr(snap, key) == p[key],
             "STOP", "STOP_MERGE_SHA_OR_TREE_DRIFT")
    need(type(snap.changed_paths) is tuple and
         all(valid_path(x) for x in snap.changed_paths) and
         len(set(snap.changed_paths)) == len(snap.changed_paths) and
         set(snap.changed_paths) == set(policy.allowed_paths),
         "DENY", "DENY_MERGE_FILE_SCOPE")
    need(p["allowed_paths_digest"] == canonical_sha256(sorted(snap.changed_paths)),
         "DENY", "DENY_MERGE_FILE_DIGEST")
    need(type(snap.raw_patch) is bytes and 0 < len(snap.raw_patch) <= policy.max_patch_bytes and
         sha256_bytes(snap.raw_patch) == p["patch_sha256"] and
         type(snap.raw_evidence) is bytes and 0 < len(snap.raw_evidence) <= policy.max_evidence_bytes and
         sha256_bytes(snap.raw_evidence) == p["evidence_sha256"],
         "DENY", "DENY_MERGE_EVIDENCE_OR_PATCH_DRIFT")
    rule = snap.rule
    need(type(rule) is SyntheticBranchRule and rule.branch == policy.base_branch and
         rule.protected is True and rule.require_pull_request is True and
         rule.require_status_checks is True and rule.require_branch_up_to_date is True and
         rule.require_conversation_resolution is True and rule.no_bypass is True and
         rule.allow_force_pushes is False and rule.allow_deletions is False and
         rule.require_linear_history is False and
         rule.require_approvals is policy.expected_require_approvals and
         rule.allowed_merge_methods == (MERGE_METHOD,),
         "HOLD", "HOLD_MERGE_BRANCH_RULE_NOT_ENFORCED")
    required = dict(policy.required_ci_apps)
    required[MERGE_CONTEXT] = registry.independent_app_id
    need(dict(rule.required_check_app_ids) == required,
         "HOLD", "HOLD_MERGE_CONTEXT_NOT_REQUIRED_BY_PROVIDER")
    need(type(snap.check_runs) is tuple and
         all(type(c) is SyntheticCheck for c in snap.check_runs),
         "HOLD", "HOLD_MERGE_CHECKS_UNTRUSTED_INPUT")
    checks = [c for c in snap.check_runs if c.name in required]
    names = [c.name for c in checks]
    need(len(names) == len(set(names)), "HOLD", "HOLD_DUPLICATE_CHECK_NAMES")
    ci = [c for c in checks if c.name in policy.required_ci_apps]
    need({c.name for c in ci} == set(policy.required_ci_apps),
         "HOLD", "HOLD_REQUIRED_CI_NOT_PRESENT")
    for c in ci:
        need(c.app_id == policy.required_ci_apps[c.name] and
             c.head_commit == p["head_commit"] and c.event == "pull_request",
             "DENY", "DENY_CI_CHECK_WRONG_APP_OR_HEAD")
        need(c.status == "completed" and c.conclusion == "success",
             "HOLD", "HOLD_CI_CHECK_NOT_SUCCESS")
    owner_check = [c for c in checks if c.name == MERGE_CONTEXT]
    if phase == "PREPARE":
        need(not owner_check, "HOLD", "HOLD_MERGE_CHECK_ALREADY_EXISTS")
    else:
        need(len(owner_check) == 1, "HOLD", "HOLD_REQUIRED_MERGE_CHECK_MISSING")
        c = owner_check[0]
        need(type(c.app_id) is int and c.app_id == registry.independent_app_id and
             c.head_commit == p["head_commit"] and c.event == "pull_request" and
             type(c.check_run_id) is int and c.check_run_id > 0 and
             c.external_id == f"{MERGE_CONTEXT}:v2:{payload_sha}",
             "DENY", "DENY_MERGE_CHECK_SOURCE_OR_BINDING")
        need(c.status == "completed" and c.conclusion == "success",
             "HOLD", "HOLD_MERGE_CHECK_NOT_SUCCESS")
        try:
            finished = utc_timestamp(c.completed_at_utc)
        except InvalidDocument as exc:
            raise GateFailure("HOLD", "HOLD_MERGE_CHECK_TIME_INVALID") from exc
        need(utc_timestamp(p["issued_at_utc"]) <= finished <= observed <= now and
             finished < utc_timestamp(p["expires_at_utc"]),
             "HOLD", "HOLD_MERGE_CHECK_TIME_DRIFT")
    need(type(snap.previews) is tuple and all(type(x) is SyntheticPreview for x in snap.previews),
         "HOLD", "HOLD_PREVIEW_EVIDENCE_MISSING")
    need(len(snap.previews) == len({x.project_id for x in snap.previews}) and
         {x.project_id for x in snap.previews} == set(policy.preview_projects),
         "HOLD", "HOLD_REQUIRED_MERGE_PREVIEWS_MISSING")
    for preview in snap.previews:
        need(preview.state == "READY" and preview.git_commit == p["head_commit"],
             "HOLD", "HOLD_MERGE_PREVIEW_NOT_READY")
    lease = snap.lease
    need(type(lease) is SyntheticLease, "HOLD", "HOLD_MERGE_LEASE_NOT_VALID")
    try:
        expiry = utc_timestamp(lease.expires_at_utc)
    except InvalidDocument as exc:
        raise GateFailure("HOLD", "HOLD_MERGE_LEASE_CLOCK_INVALID") from exc
    need(expiry > now and lease.conflict_free is True and
         lease.coordination_ref_sha == p["coordination_ref_sha"] and
         lease.target_repo == p["repo"] and lease.target_pr == p["pr"] and
         lease.target_head_commit == p["head_commit"] and lease.authorized_action == ACTION,
         "HOLD", "HOLD_MERGE_LEASE_NOT_EXACT")


def evaluate_merge_only(envelope_bytes: bytes, *, registry: SyntheticOwnerRegistry | None,
                        policy: SyntheticMergePolicy, provider: SyntheticProviderSnapshot | None,
                        ledger: SyntheticMergeLedger | None, now_utc: datetime,
                        requested_action: str = ACTION, phase: str = "PREPARE") -> MergeTestReceipt:
    """Synthetic v2 CHECK_PREPARE or JIT_EXECUTION admission; real actions DENIED.

    PREPARE: atomically consumes an owner-preissued test nonce, never publishes a
    real GitHub check. JIT_EXECUTION: reads back consumed ledger + completed
    source-pinned synthetic check and revalidates current timestamp/snapshot.
    No real GitHub merge is possible from this function.
    """
    payload_sha: str | None = None
    fingerprint: str | None = None
    try:
        need(phase in ("PREPARE", "JIT_EXECUTION"), "DENY", "DENY_UNKNOWN_MERGE_PHASE")
        _policy(policy, requested_action)
        try:
            envelope = strict_json_bytes(envelope_bytes)
        except InvalidDocument as exc:
            raise GateFailure("DENY", "DENY_INVALID_MERGE_JSON") from exc
        p = _payload(envelope)
        payload_sha = canonical_sha256(p)
        need(p["repo"] == policy.repo and p["pr"] == policy.pr and
             p["base_branch"] == policy.base_branch and
             p["merge_method"] == policy.merge_method,
             "STOP", "STOP_MERGE_POLICY_TARGET_DRIFT")
        need(p["action"] == requested_action, "DENY", "DENY_MERGE_ACTION_MISMATCH")
        fingerprint = _registry(p, envelope, registry, dict(policy.required_ci_apps))
        _time(p, policy, now_utc)
        _provider(p, policy, registry, provider, now_utc, phase, payload_sha)
        need(type(ledger) is SyntheticMergeLedger and ledger.ledger_id == policy.ledger_id,
             "HOLD", "HOLD_INDEPENDENT_MERGE_LEDGER_UNIMPLEMENTED")
        try:
            ledger_kwargs = dict(
                issuer_key_id=p["issuer_key_id"], nonce=p["nonce"],
                repo=p["repo"], pr=p["pr"], payload_sha256=payload_sha,
                base_commit=p["base_commit"], head_commit=p["head_commit"],
                expires_at_utc=p["expires_at_utc"])
            if phase == "PREPARE":
                ledger.consume(**ledger_kwargs, consumed_at=now_utc)
            else:
                need(ledger.verify_consumed(**ledger_kwargs),
                     "HOLD", "HOLD_MERGE_NONCE_CONSUMPTION_NOT_VERIFIED")
        except MergeNonceReplayed as exc:
            raise GateFailure("DENY", "DENY_MERGE_NONCE_REPLAY") from exc
        except MergeNonceNotIssued as exc:
            raise GateFailure("DENY", "DENY_MERGE_NONCE_NOT_PREISSUED") from exc
        except MergeLedgerError as exc:
            raise GateFailure("HOLD", "HOLD_MERGE_LEDGER_UNAVAILABLE") from exc
        return MergeTestReceipt(
            "TEST_ONLY_PASS",
            "PASS_SYNTHETIC_CHECK_PREPARE_ONLY" if phase == "PREPARE" else
            "PASS_SYNTHETIC_JIT_REVALIDATION_ONLY",
            phase,
            nonce_consumed=(phase == "PREPARE"), payload_sha256=payload_sha,
            owner_public_fingerprint_sha256=fingerprint,
        )
    except GateFailure as exc:
        return MergeTestReceipt(exc.status, exc.code, phase, payload_sha256=payload_sha,
                                owner_public_fingerprint_sha256=fingerprint)
    except (InvalidDocument, AttributeError, TypeError, ValueError, OverflowError,
            KeyError) as exc:
        return MergeTestReceipt("DENY", "DENY_SYNTHETIC_MERGE_CONTRACT_INVALID",
                                phase, payload_sha256=payload_sha,
                                owner_public_fingerprint_sha256=fingerprint)
