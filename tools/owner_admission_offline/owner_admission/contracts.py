"""Immutable test-only data contracts; no provider client or credentials."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Mapping


@dataclass(frozen=True)
class CheckRun:
    name: str
    app_id: int
    head_commit: str
    status: str
    conclusion: str
    event: str


@dataclass(frozen=True)
class Preview:
    project_id: str
    state: str
    git_commit: str


@dataclass(frozen=True)
class BranchRule:
    protected: bool
    require_pull_request: bool
    require_status_checks: bool
    require_branch_up_to_date: bool
    require_conversation_resolution: bool
    no_bypass: bool
    allow_force_pushes: bool
    allow_deletions: bool
    require_linear_history: bool
    required_check_app_ids: Mapping[str, int]
    # In production, fields MUST be fetched via separately authenticated App.
    # A Python bool here cannot prove authenticated provider provenance.


@dataclass(frozen=True)
class LeaseEvidence:
    coordination_ref_sha: str
    expires_at_utc: str
    target_repo: str
    target_head_commit: str
    authorized_action: str
    conflict_free: bool


@dataclass(frozen=True)
class ProviderSnapshot:
    repo: str
    pr: int
    base_commit: str
    base_tree: str
    head_commit: str
    head_tree: str
    state: str
    draft: bool
    observed_at_utc: str
    changed_paths: tuple[str, ...]
    raw_patch: bytes
    raw_evidence: bytes
    check_runs: tuple[CheckRun, ...]
    previews: tuple[Preview, ...]
    rule: BranchRule
    lease: LeaseEvidence
    # Explicitly synthetic: no live provider API trust is established here.


@dataclass(frozen=True)
class TrustRegistry:
    owner_public_keys: Mapping[str, bytes]
    revoked_owner_key_ids: frozenset[str]
    independent_app_id: int
    registry_version: str
    # Caller MUST control these independently of candidate PR; not yet installed.


@dataclass(frozen=True)
class TestPolicy:
    repo: str
    pr: int
    policy_version: str
    allowed_paths: tuple[str, ...]
    required_ci_app_ids: Mapping[str, int]
    preview_project_ids: tuple[str, ...]
    max_ttl_seconds: int
    max_future_skew_seconds: int
    max_provider_age_seconds: int
    max_patch_bytes: int
    max_evidence_bytes: int
    approved_action: str = "MARK_READY_ONLY"
    review_mode: str = "SOURCE_ONLY_NO_RELEASE"
    audience: str = "OFFLINE_TEST_ONLY"
    # Explicitly cannot become production authorization by changing a flag.
