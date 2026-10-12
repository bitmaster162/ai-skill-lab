"""AI Skill Lab R4F7F isolated, test-only owner-admission contract.

This package cannot approve a real merge, publish a check, generate an owner
private key, or access GitHub. Passing results are ALWAYS test-only.
"""

from .verifier import evaluate, EvaluationReceipt
from .contracts import (
    BranchRule, CheckRun, LeaseEvidence, Preview, ProviderSnapshot,
    TestPolicy, TrustRegistry,
)
from .ledger import SqliteNonceLedger, NonceLedgerError, bootstrap_test_ledger

__all__ = [
    "evaluate", "EvaluationReceipt", "BranchRule", "CheckRun", "LeaseEvidence",
    "Preview", "ProviderSnapshot", "TestPolicy", "TrustRegistry",
    "SqliteNonceLedger", "NonceLedgerError", "bootstrap_test_ledger",
]
