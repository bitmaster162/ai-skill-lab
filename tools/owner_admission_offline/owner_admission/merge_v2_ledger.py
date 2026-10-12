"""R4F7H offline TEST nonce register, one-time consume and readback.

Schema deliberately differs from R4F7F. It models a UNIQUE issuer+nonce
independent of action. A production shared ledger/recovery protocol is NOT
implemented and an sqlite test DB is not a secure owner trust domain.
"""
from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path
import sqlite3
import stat

SCHEMA = "ai-skill-lab.r4f7h.test-ledger.v2"


class MergeLedgerError(Exception):
    pass


class MergeNonceNotIssued(MergeLedgerError):
    pass


class MergeNonceReplayed(MergeLedgerError):
    pass


class SyntheticMergeLedger:
    def __init__(self, file_path: str, ledger_id: str):
        self.file_path = Path(file_path)
        self.ledger_id = ledger_id

    def _connect(self) -> sqlite3.Connection:
        path = self.file_path
        if not path.is_absolute() or path.is_symlink() or not path.is_file():
            raise MergeLedgerError("LEDGER_MISSING_OR_UNSAFE_PATH")
        try:
            if not stat.S_ISREG(os.stat(path, follow_symlinks=False).st_mode):
                raise MergeLedgerError("LEDGER_NOT_REGULAR")
            conn = sqlite3.connect(path.as_uri() + "?mode=rw", uri=True,
                                   timeout=0, isolation_level=None)
            try:
                values = dict(conn.execute("SELECT key,value FROM metadata").fetchall())
                if (values.get("schema") != SCHEMA or
                        values.get("ledger_id") != self.ledger_id):
                    raise MergeLedgerError("LEDGER_SCHEMA_OR_ID_MISMATCH")
            except (sqlite3.Error, MergeLedgerError):
                conn.close()
                raise
            return conn
        except (sqlite3.Error, OSError) as exc:
            raise MergeLedgerError("LEDGER_UNAVAILABLE") from exc

    @staticmethod
    def _record(issuer_key_id: str, nonce: str, repo: str, pr: int,
                payload_sha256: str, base_commit: str, head_commit: str,
                expires_at_utc: str) -> tuple:
        return (issuer_key_id, nonce, repo, pr, "MERGE_ONLY", payload_sha256,
                base_commit, head_commit, expires_at_utc)

    def preissue_for_test(self, *, issuer_key_id: str, nonce: str, repo: str,
                          pr: int, action: str, payload_sha256: str,
                          base_commit: str, head_commit: str,
                          expires_at_utc: str, test_mode: bool = False) -> None:
        """Synthetic pre-issuance ONLY; not a callable production signer/issuer."""
        if test_mode is not True:
            raise MergeLedgerError("PREISSUE_TEST_MODE_REQUIRED")
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "INSERT INTO issued VALUES (?,?,?,?,?,?,?,?,?)",
                (issuer_key_id, nonce, repo, pr, action, payload_sha256,
                 base_commit, head_commit, expires_at_utc))
            conn.execute("COMMIT")
        except sqlite3.IntegrityError as exc:
            conn.execute("ROLLBACK")
            raise MergeNonceReplayed("NONCE_UNIQUE_ACROSS_ACTIONS") from exc
        except sqlite3.Error as exc:
            conn.execute("ROLLBACK")
            raise MergeLedgerError("LEDGER_PREISSUE_FAILURE") from exc
        finally:
            conn.close()

    def consume(self, *, issuer_key_id: str, nonce: str, repo: str, pr: int,
                payload_sha256: str, base_commit: str, head_commit: str,
                expires_at_utc: str, consumed_at: datetime) -> None:
        expected = self._record(issuer_key_id, nonce, repo, pr, payload_sha256,
                                base_commit, head_commit, expires_at_utc)
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            issued = conn.execute(
                "SELECT issuer_key_id, nonce, repo, pr, action, payload_sha256, "
                "base_commit, head_commit, expires_at_utc FROM issued "
                "WHERE issuer_key_id=? AND nonce=?", (issuer_key_id, nonce)).fetchone()
            if issued != expected:
                raise MergeNonceNotIssued("NONCE_UNISSUED_OR_ACTION_OR_PAYLOAD_DRIFT")
            cur = conn.execute(
                "INSERT OR IGNORE INTO consumed VALUES (?,?,?,?)",
                (issuer_key_id, nonce, payload_sha256,
                 consumed_at.strftime("%Y-%m-%dT%H:%M:%SZ")))
            if cur.rowcount != 1:
                raise MergeNonceReplayed("NONCE_ALREADY_CONSUMED")
            conn.execute("COMMIT")
        except (MergeNonceNotIssued, MergeNonceReplayed):
            conn.execute("ROLLBACK")
            raise
        except sqlite3.Error as exc:
            try:
                conn.execute("ROLLBACK")
            except sqlite3.Error:
                pass
            raise MergeLedgerError("LEDGER_CONSUME_FAILURE") from exc
        finally:
            conn.close()

    def verify_consumed(self, *, issuer_key_id: str, nonce: str, repo: str,
                        pr: int, payload_sha256: str, base_commit: str,
                        head_commit: str, expires_at_utc: str) -> bool:
        """Read-only check for consumed nonce. Cannot attest backup monotonicity."""
        expected = self._record(issuer_key_id, nonce, repo, pr, payload_sha256,
                                base_commit, head_commit, expires_at_utc)
        conn = self._connect()
        try:
            issued = conn.execute(
                "SELECT issuer_key_id, nonce, repo, pr, action, payload_sha256, "
                "base_commit, head_commit, expires_at_utc FROM issued "
                "WHERE issuer_key_id=? AND nonce=?", (issuer_key_id, nonce)).fetchone()
            consumed = conn.execute(
                "SELECT payload_sha256, consumed_at_utc FROM consumed "
                "WHERE issuer_key_id=? AND nonce=?", (issuer_key_id, nonce)).fetchone()
            return (issued == expected and consumed is not None and
                    consumed[0] == payload_sha256)
        except sqlite3.Error as exc:
            raise MergeLedgerError("LEDGER_READBACK_FAILURE") from exc
        finally:
            conn.close()


def bootstrap_synthetic_merge_ledger(path: str, ledger_id: str,
                                      *, test_mode: bool = False) -> None:
    if test_mode is not True:
        raise MergeLedgerError("TEST_BOOTSTRAP_REQUIRED")
    p = Path(path)
    if not p.is_absolute() or p.exists() or p.is_symlink():
        raise MergeLedgerError("NEW_ABSOLUTE_PATH_REQUIRED")
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p), timeout=0)
    try:
        conn.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        conn.executemany("INSERT INTO metadata VALUES (?,?)",
                         [("schema", SCHEMA), ("ledger_id", ledger_id)])
        conn.execute("CREATE TABLE issued ("
                     "issuer_key_id TEXT NOT NULL, nonce TEXT NOT NULL, repo TEXT NOT NULL, "
                     "pr INTEGER NOT NULL, action TEXT NOT NULL, payload_sha256 TEXT NOT NULL, "
                     "base_commit TEXT NOT NULL, head_commit TEXT NOT NULL, "
                     "expires_at_utc TEXT NOT NULL, PRIMARY KEY(issuer_key_id,nonce))")
        conn.execute("CREATE TABLE consumed ("
                     "issuer_key_id TEXT NOT NULL, nonce TEXT NOT NULL, "
                     "payload_sha256 TEXT NOT NULL, consumed_at_utc TEXT NOT NULL, "
                     "PRIMARY KEY(issuer_key_id,nonce))")
        conn.commit()
    finally:
        conn.close()
