"""R4F7H production-boundary stub: no live provider adapter is installed.

The public type is intentionally *not* a drop-in GitHub/Vercel client.
Every method refuses to fetch, publish a required check, mark ready, merge,
or publish. No credentials, URL, token, network, SDK or mode switch exists.
Tests directly exercise these explicit unimplemented boundaries.
"""
from __future__ import annotations


class IndependentProviderNotInstalled(RuntimeError):
    pass


class DisabledIndependentProviderPort:
    def read_authenticated_snapshot(self, *, repo: str, pr: int):
        raise IndependentProviderNotInstalled("AUTHENTICATED_PROVIDER_READBACK_UNIMPLEMENTED")

    def publish_source_pinned_merge_check(self, *, repo: str, commit: str, receipt: bytes):
        raise IndependentProviderNotInstalled("INDEPENDENT_GITHUB_APP_CHECK_UNIMPLEMENTED")

    def execute_merge(self, *, repo: str, pr: int, expected_head: str):
        raise IndependentProviderNotInstalled("REAL_MERGE_EXECUTOR_UNIMPLEMENTED")

    def mark_ready(self, *, repo: str, pr: int):
        raise IndependentProviderNotInstalled("MARK_READY_ACTION_NOT_SUPPORTED")

    def deploy(self, *, release: str):
        raise IndependentProviderNotInstalled("PRODUCTION_PUBLICATION_NOT_SUPPORTED")
