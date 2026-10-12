"""R4F7H merge-only synthetic contracts, independent from R4F7F MARK_READY.

ALL values are untrusted test inputs. No object defined here represents an
authenticated provider assertion or an operator's authorization.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class SyntheticCheck:
    name: str
    app_id: int
    head_commit: str
    status: str
    conclusion: str
    event: str
    check_run_id: int = 0
    external_id: str = ""
    completed_at_utc: str = ""


@dataclass(frozen=True)
class SyntheticPreview:
    project_id: str
    git_commit: str
    state: str


@dataclass(frozen=True)
class SyntheticBranchRule:
    branch: str
    protected: bool
    require_pull_request: bool
    require_status_checks: bool
    require_branch_up_to_date: bool
    require_conversation_resolution: bool
    no_bypass: bool
    allow_force_pushes: bool
    allow_deletions: bool
    require_linear_history: bool
    require_approvals: bool
    allowed_merge_methods: tuple[str, ...]
    required_check_app_ids: Mapping[str, int]


@dataclass(frozen=True)
class SyntheticLease:
    coordination_ref_sha: str
    expires_at_utc: str
    target_repo: str
    target_pr: int
    target_head_commit: str
    authorized_action: str
    conflict_free: bool


@dataclass(frozen=True)
class SyntheticProviderSnapshot:
    """Unauthenticated readback-shaped test data: NEVER use for real GitHub actions."""
    source: str
    repo: str
    pr: int
    branch: str
    base_commit: str
    base_tree: str
    head_commit: str
    head_tree: str
    state: str
    draft: bool
    mergeable: bool
    observed_at_utc: str
    changed_paths: tuple[str, ...]
    raw_patch: bytes
    raw_evidence: bytes
    check_runs: tuple[SyntheticCheck, ...]
    previews: tuple[SyntheticPreview, ...]
    rule: SyntheticBranchRule
    lease: SyntheticLease


@dataclass(frozen=True)
class SyntheticMergePolicy:
    """A value supplied by a TEST, never a deployed trusted policy registry."""
    repo: str
    pr: int
    base_branch: str
    policy_version: str
    allowed_paths: tuple[str, ...]
    required_ci_apps: Mapping[str, int]
    preview_projects: tuple[str, ...]
    expected_require_approvals: bool
    max_ttl_seconds: int
    max_future_skew_seconds: int
    max_provider_age_seconds: int
    max_patch_bytes: int
    max_evidence_bytes: int
    ledger_id: str
    audience: str = "OFFLINE_TEST_ONLY"
    action: str = "MERGE_ONLY"
    merge_method: str = "merge"


@dataclass(frozen=True)
class SyntheticOwnerRegistry:
    public_keys: Mapping[str, bytes]
    revoked_ids: frozenset[str]
    independent_app_id: int
    version: str
    # For real use this MUST be outside the target repo and under owner control.
