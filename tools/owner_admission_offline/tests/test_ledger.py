import sqlite3
import tempfile
import unittest
from pathlib import Path

from owner_admission.ledger import (
    NonceLedgerError, NonceNotIssued, NonceReplayed, SqliteNonceLedger, bootstrap_test_ledger,
)
from tests.support import NOW


class LedgerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="r4f7f-ledger-")
        self.db = str(Path(self.tmp.name) / "nonce.db")

    def tearDown(self):
        self.tmp.cleanup()

    def test_cannot_bootstrap_without_explicit_test_mode(self):
        with self.assertRaises(NonceLedgerError):
            bootstrap_test_ledger(self.db)
        self.assertFalse(Path(self.db).exists())

    def test_no_implicit_file_creation(self):
        with self.assertRaises(NonceLedgerError):
            SqliteNonceLedger(self.db).consume(
                issuer_key_id="synthetic", nonce="a", payload_sha256="a"*64,
                action="MARK_READY_ONLY", head_commit="b"*40, expires_at_utc="2026-10-12T13:10:00Z", consumed_at=NOW)
        self.assertFalse(Path(self.db).exists())

    def test_consumed_once_sqlite_cas(self):
        bootstrap_test_ledger(self.db, test_mode=True)
        c = SqliteNonceLedger(self.db)
        args=dict(issuer_key_id="synthetic", nonce="a"*32,
                  payload_sha256="b"*64, action="MARK_READY_ONLY",
                  head_commit="c"*40, expires_at_utc="2026-10-12T13:10:00Z", consumed_at=NOW)
        conn=sqlite3.connect(self.db)
        conn.execute("INSERT INTO issued VALUES (?,?,?,?,?,?)",
                     (args["issuer_key_id"],args["nonce"],args["payload_sha256"],
                      args["action"],args["head_commit"],args["expires_at_utc"]))
        conn.commit();conn.close()
        c.consume(**args)
        with self.assertRaises(NonceReplayed):
            SqliteNonceLedger(self.db).consume(**args)
        conn=sqlite3.connect(self.db)
        self.assertEqual(conn.execute("SELECT count(*) FROM consumed").fetchone(), (1,))
        conn.close()

    def test_unissued_nonce_rejected(self):
        bootstrap_test_ledger(self.db, test_mode=True)
        with self.assertRaises(NonceNotIssued):
            SqliteNonceLedger(self.db).consume(
                issuer_key_id="synthetic", nonce="a"*32, payload_sha256="b"*64,
                action="MARK_READY_ONLY", head_commit="c"*40,
                expires_at_utc="2026-10-12T13:10:00Z", consumed_at=NOW)

    def test_test_ledger_refuses_existing_path(self):
        bootstrap_test_ledger(self.db, test_mode=True)
        with self.assertRaises(NonceLedgerError):
            bootstrap_test_ledger(self.db, test_mode=True)

    def test_schema_version_drift_denied(self):
        bootstrap_test_ledger(self.db, test_mode=True)
        db=sqlite3.connect(self.db)
        db.execute("UPDATE ledger_meta SET value='obsolete'")
        db.commit();db.close()
        with self.assertRaises(NonceLedgerError):
            SqliteNonceLedger(self.db).consume(
                issuer_key_id="synthetic", nonce="a"*32, payload_sha256="b"*64,
                action="MARK_READY_ONLY", head_commit="c"*40,
                expires_at_utc="2026-10-12T13:10:00Z", consumed_at=NOW)

    def test_unexpected_schema_fail_closed(self):
        Path(self.db).write_bytes(b"invalid")
        with self.assertRaises(NonceLedgerError):
            SqliteNonceLedger(self.db).consume(
                issuer_key_id="synthetic", nonce="a", payload_sha256="a"*64,
                action="MARK_READY_ONLY", head_commit="b"*40, expires_at_utc="2026-10-12T13:10:00Z", consumed_at=NOW)

    def test_consumption_atomic_across_connections(self):
        bootstrap_test_ledger(self.db, test_mode=True)
        args=dict(issuer_key_id="synthetic", nonce="a"*32,
                  payload_sha256="b"*64, action="MARK_READY_ONLY",
                  head_commit="c"*40, expires_at_utc="2026-10-12T13:10:00Z", consumed_at=NOW)
        c1 = SqliteNonceLedger(self.db)
        c2 = SqliteNonceLedger(self.db)
        conn=sqlite3.connect(self.db)
        conn.execute("INSERT INTO issued VALUES (?,?,?,?,?,?)",
                     (args["issuer_key_id"],args["nonce"],args["payload_sha256"],
                      args["action"],args["head_commit"],args["expires_at_utc"]))
        conn.commit();conn.close()
        c1.consume(**args)
        with self.assertRaises(NonceReplayed):
            c2.consume(**args)


if __name__ == "__main__":
    unittest.main()
