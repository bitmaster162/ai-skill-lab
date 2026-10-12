"""Disposable v2 SQLite nonce contract, including concurrency and action isolation."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import os
import sqlite3
import tempfile
import unittest

from owner_admission.canonical import canonical_sha256
from owner_admission.merge_v2_ledger import (
    MergeLedgerError, MergeNonceNotIssued, MergeNonceReplayed,
    SyntheticMergeLedger, bootstrap_synthetic_merge_ledger,
)
from tests.merge_v2_support import MergeFixture, NOW


class TestMergeLedger(unittest.TestCase):
    def setUp(self):
        self.f=MergeFixture()
        self.addCleanup(self.f.close)
        p=self.f.payload
        self.params=dict(issuer_key_id=p["issuer_key_id"],nonce=p["nonce"],
                         repo=p["repo"],pr=p["pr"],payload_sha256=canonical_sha256(p),
                         base_commit=p["base_commit"],head_commit=p["head_commit"],
                         expires_at_utc=p["expires_at_utc"])

    def test_preissuance_precedes_consumption(self):
        self.assertFalse(self.f.ledger.verify_consumed(**self.params))
        self.f.ledger.consume(**self.params,consumed_at=NOW)
        self.assertTrue(self.f.ledger.verify_consumed(**self.params))

    def test_nonce_cannot_be_consumed_twice(self):
        self.f.ledger.consume(**self.params,consumed_at=NOW)
        with self.assertRaises(MergeNonceReplayed):
            self.f.ledger.consume(**self.params,consumed_at=NOW)

    def test_nonce_commitment_head_scope(self):
        with self.assertRaises(MergeNonceNotIssued):
            self.f.ledger.consume(**{**self.params,"head_commit":"0"*40},consumed_at=NOW)
        self.assertFalse(self.f.ledger.verify_consumed(**self.params))

    def test_nonce_commitment_repository_scope(self):
        with self.assertRaises(MergeNonceNotIssued):
            self.f.ledger.consume(**{**self.params,"repo":"other/repo"},consumed_at=NOW)

    def test_nonce_commitment_base_scope(self):
        with self.assertRaises(MergeNonceNotIssued):
            self.f.ledger.consume(**{**self.params,"base_commit":"0"*40},consumed_at=NOW)

    def test_nonce_commitment_payload_scope(self):
        with self.assertRaises(MergeNonceNotIssued):
            self.f.ledger.consume(**{**self.params,"payload_sha256":"0"*64},consumed_at=NOW)

    def test_nonce_commitment_expiry_scope(self):
        with self.assertRaises(MergeNonceNotIssued):
            self.f.ledger.consume(**{**self.params,"expires_at_utc":"2026-10-12T13:05:00Z"},consumed_at=NOW)

    def test_issued_under_mark_ready_cannot_be_consumed_as_merge(self):
        with closing(sqlite3.connect(self.f.ledger_path)) as db, db:
            db.execute("UPDATE issued SET action='MARK_READY_ONLY'")
        with self.assertRaises(MergeNonceNotIssued):
            self.f.ledger.consume(**self.params,consumed_at=NOW)

    def test_same_nonce_cannot_be_preissued_for_different_action(self):
        with self.assertRaises(MergeNonceReplayed):
            self.f.ledger.preissue_for_test(
                **self.params,action="MARK_READY_ONLY",test_mode=True)

    def test_second_nonce_after_merge_needs_separate_preissuance(self):
        with self.assertRaises(MergeNonceNotIssued):
            self.f.ledger.consume(**{**self.params,"nonce":"b"*32},consumed_at=NOW)

    def test_missing_consumed_row_detected_during_readback(self):
        self.f.ledger.consume(**self.params,consumed_at=NOW)
        with closing(sqlite3.connect(self.f.ledger_path)) as db, db:
            db.execute("DELETE FROM consumed")
        self.assertFalse(self.f.ledger.verify_consumed(**self.params))

    def test_forged_consumed_without_issued_commitment_denied(self):
        with closing(sqlite3.connect(self.f.ledger_path)) as db, db:
            db.execute("INSERT INTO consumed VALUES (?,?,?,?)",
                       (self.params["issuer_key_id"],self.params["nonce"],
                        self.params["payload_sha256"],"2026-10-12T13:01:00Z"))
            db.execute("DELETE FROM issued")
        self.assertFalse(self.f.ledger.verify_consumed(**self.params))

    def test_ledger_schema_metadata_corruption_denied(self):
        with closing(sqlite3.connect(self.f.ledger_path)) as db, db:
            db.execute("UPDATE metadata SET value='r4f7f.test.v1' WHERE key='schema'")
        with self.assertRaises(MergeLedgerError):
            self.f.ledger.consume(**self.params,consumed_at=NOW)

    def test_ledger_identifier_corruption_denied(self):
        with closing(sqlite3.connect(self.f.ledger_path)) as db, db:
            db.execute("UPDATE metadata SET value='WRONG' WHERE key='ledger_id'")
        with self.assertRaises(MergeLedgerError):
            self.f.ledger.verify_consumed(**self.params)

    def test_bootstrap_without_test_mode_denied(self):
        with self.assertRaises(MergeLedgerError):
            bootstrap_synthetic_merge_ledger(os.path.join(self.f.dir.name,"other.sqlite"),
                                             "test-ledger",test_mode=False)

    def test_bootstrap_cannot_overwrite_existing_ledger(self):
        with self.assertRaises(MergeLedgerError):
            bootstrap_synthetic_merge_ledger(self.f.ledger_path,"test-ledger",test_mode=True)

    def test_bootstrap_relative_path_denied(self):
        with self.assertRaises(MergeLedgerError):
            bootstrap_synthetic_merge_ledger("my-ledger.db","test-ledger",test_mode=True)

    def test_preissue_requires_explicit_test_mode(self):
        with self.assertRaises(MergeLedgerError):
            self.f.ledger.preissue_for_test(**self.params,action="MERGE_ONLY")

    def test_missing_ledger_file_holds(self):
        wrong=SyntheticMergeLedger(os.path.join(self.f.dir.name,"missing.db"),
                                   self.f.ledger.ledger_id)
        with self.assertRaises(MergeLedgerError):
            wrong.consume(**self.params,consumed_at=NOW)

    def test_symlink_ledger_holds(self):
        target=os.path.join(self.f.dir.name,"linked.sqlite")
        os.symlink(self.f.ledger_path,target)
        linked=SyntheticMergeLedger(target,self.f.ledger.ledger_id)
        with self.assertRaises(MergeLedgerError):
            linked.verify_consumed(**self.params)

    def test_two_consumer_race_at_most_one_success(self):
        def task(_):
            try:
                self.f.ledger.consume(**self.params,consumed_at=NOW)
                return "PASS"
            except (MergeLedgerError, MergeNonceReplayed):
                return "BLOCKED"
        with ThreadPoolExecutor(max_workers=2) as pool:
            res=list(pool.map(task,range(2)))
        # Zero successes under timeout=0 is acceptable fail-closed contention.
        # What matters: never two successes and no unrecorded consumption.
        self.assertLessEqual(res.count("PASS"),1)
        self.assertEqual(res.count("PASS")+res.count("BLOCKED"),2)
        with closing(sqlite3.connect(self.f.ledger_path)) as db, db:
            committed = db.execute("SELECT count(*) FROM consumed").fetchone()[0]
        self.assertEqual(committed,res.count("PASS"))

    def test_sqlite_preissue_table_missing_holds(self):
        with closing(sqlite3.connect(self.f.ledger_path)) as db, db:
            db.execute("DROP TABLE issued")
        with self.assertRaises(MergeLedgerError):
            self.f.ledger.preissue_for_test(**{**self.params,"nonce":"f"*32},
                                            action="MERGE_ONLY",test_mode=True)

    def test_sqlite_consume_table_missing_holds(self):
        with closing(sqlite3.connect(self.f.ledger_path)) as db, db:
            db.execute("DROP TABLE consumed")
        with self.assertRaises(MergeLedgerError):
            self.f.ledger.consume(**self.params,consumed_at=NOW)

    def test_sqlite_consumed_readback_missing_holds(self):
        with closing(sqlite3.connect(self.f.ledger_path)) as db, db:
            db.execute("DROP TABLE consumed")
        with self.assertRaises(MergeLedgerError):
            self.f.ledger.verify_consumed(**self.params)

    def test_bad_database_bytes_fail_closed(self):
        with open(self.f.ledger_path,"wb") as fh:
            fh.write(b"not a valid sqlite file")
        with self.assertRaises(MergeLedgerError):
            self.f.ledger.verify_consumed(**self.params)


if __name__=="__main__":
    unittest.main()
