"""Atomic independent nonce ledger contract; opens an EXISTING SQLite file.

The verifier never bootstraps a ledger or creates it during evaluation.
`bootstrap_test_ledger` is explicit and forbidden outside disposable test dirs.
No production DB location / service / trust domain is configured here.
"""
from __future__ import annotations
import os
import sqlite3
import stat
from datetime import datetime
from pathlib import Path


class NonceLedgerError(Exception):
    pass


class NonceReplayed(NonceLedgerError):
    pass


class NonceNotIssued(NonceLedgerError):
    pass


class SqliteNonceLedger:
    def __init__(self, path: str):
        self.path = Path(path)

    def consume(self, *, issuer_key_id: str, nonce: str, payload_sha256: str,
                action: str, head_commit: str, expires_at_utc: str,
                consumed_at: datetime) -> None:
        if not self.path.is_absolute() or self.path.is_symlink() or not self.path.is_file():
            raise NonceLedgerError("LEDGER_MISSING_OR_UNSAFE_PATH")
        if not stat.S_ISREG(os.stat(self.path, follow_symlinks=False).st_mode):
            raise NonceLedgerError("LEDGER_NOT_REGULAR_FILE")
        uri = self.path.as_uri() + "?mode=rw"
        try:
            conn = sqlite3.connect(uri, uri=True, timeout=0, isolation_level=None)
        except (sqlite3.Error, OSError) as exc:
            raise NonceLedgerError("LEDGER_UNAVAILABLE") from exc
        try:
            try:
                conn.execute("BEGIN IMMEDIATE")
                meta = conn.execute("SELECT value FROM ledger_meta WHERE key='schema_version'").fetchone()
                if meta != ("r4f7f.test.v1",):
                    raise NonceLedgerError("LEDGER_SCHEMA_UNTRUSTED")
                # A nonce must have been pre-issued by the independently controlled
                # ledger, and committed to this precise signed payload. Merely
                # choosing a new random nonce cannot establish owner issuance.
                issued = conn.execute(
                    "SELECT payload_sha256, action, head_commit, expires_at_utc "
                    "FROM issued WHERE issuer_key_id=? AND nonce=?",
                    (issuer_key_id, nonce)).fetchone()
                if issued != (payload_sha256, action, head_commit, expires_at_utc):
                    raise NonceNotIssued("NONCE_NOT_IN_PREISSUED_LEDGER_OR_SCOPE_DRIFT")
                cur = conn.execute(
                    "INSERT OR IGNORE INTO consumed "
                    "(issuer_key_id, nonce, payload_sha256, action, head_commit, consumed_at_utc) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (issuer_key_id, nonce, payload_sha256, action, head_commit,
                     consumed_at.strftime("%Y-%m-%dT%H:%M:%SZ")))
                if cur.rowcount != 1:
                    raise NonceReplayed("NONCE_ALREADY_CONSUMED")
                conn.execute("COMMIT")
            except (NonceLedgerError, sqlite3.Error):
                try:
                    conn.execute("ROLLBACK")
                except sqlite3.Error:
                    pass  # Ledger stays fail-closed if transaction never began.
                raise
        except sqlite3.Error as exc:
            raise NonceLedgerError("LEDGER_SQLITE_FAILURE") from exc
        finally:
            conn.close()


def bootstrap_test_ledger(path: str, *, test_mode: bool = False) -> None:
    if test_mode is not True:
        raise NonceLedgerError("TEST_BOOTSTRAP_REQUIRES_EXPLICIT_TEST_MODE")
    p = Path(path)
    if not p.is_absolute() or p.exists() or p.is_symlink():
        raise NonceLedgerError("TEST_BOOTSTRAP_NEW_ABSOLUTE_PATH_REQUIRED")
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p), timeout=0)
    try:
        conn.execute("CREATE TABLE ledger_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        conn.execute("INSERT INTO ledger_meta VALUES ('schema_version', 'r4f7f.test.v1')")
        conn.execute("CREATE TABLE issued ("
                     "issuer_key_id TEXT NOT NULL, nonce TEXT NOT NULL, "
                     "payload_sha256 TEXT NOT NULL, action TEXT NOT NULL, "
                     "head_commit TEXT NOT NULL, expires_at_utc TEXT NOT NULL, "
                     "PRIMARY KEY(issuer_key_id, nonce))")
        conn.execute("CREATE TABLE consumed ("
                     "issuer_key_id TEXT NOT NULL, nonce TEXT NOT NULL, "
                     "payload_sha256 TEXT NOT NULL, action TEXT NOT NULL, "
                     "head_commit TEXT NOT NULL, consumed_at_utc TEXT NOT NULL, "
                     "PRIMARY KEY(issuer_key_id, nonce))")
        conn.commit()
    finally:
        conn.close()
