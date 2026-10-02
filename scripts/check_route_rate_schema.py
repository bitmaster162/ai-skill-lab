#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import sqlite3
import unittest
import uuid

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=ROOT/"schema/route_rate_event_r159.sql"
WORKER=ROOT/"services/lead-receiver-cloudflare/src/index.js"
SCHEMA_SHA256="29b29345e398b2724d7a3330a71bae39b310f999fddf6b745b5e414b05b643f4"
HOUR=3600
DAY=86400
HOURLY_LIMIT=5

INSERT_SQL="""
INSERT INTO route_rate_event_r159 (request_id, ip_token, occurred_at)
SELECT ?, ?, ?
WHERE
  (SELECT COUNT(*) FROM route_rate_event_r159 WHERE ip_token = ? AND occurred_at >= ?) < ?
  AND
  (SELECT COUNT(*) FROM route_rate_event_r159 WHERE occurred_at >= ?) < ?
ON CONFLICT(request_id) DO NOTHING
"""

class RouteRateSchemaTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(":memory:")
        self.addCleanup(self.db.close)
        self.db.executescript(SCHEMA.read_text(encoding="utf-8"))

    def insert(self, ip_token, now, daily_limit=77, request_id=None):
        request_id=request_id or str(uuid.uuid4())
        return self.db.execute(
            INSERT_SQL,
            (
                request_id,ip_token,now,
                ip_token,now-HOUR,HOURLY_LIMIT,
                now-DAY,daily_limit,
            ),
        ).rowcount

    def test_snapshot_fingerprint(self):
        self.assertEqual(hashlib.sha256(SCHEMA.read_bytes()).hexdigest(),SCHEMA_SHA256)

    def test_schema_and_indexes(self):
        cols=self.db.execute("PRAGMA table_info(route_rate_event_r159)").fetchall()
        self.assertEqual([x[1] for x in cols],["request_id","ip_token","occurred_at"])
        self.assertEqual([x[1] for x in cols if x[5]],["request_id"])
        indexes={x[1] for x in self.db.execute("PRAGMA index_list(route_rate_event_r159)").fetchall()}
        self.assertIn("route_rate_event_r159_ip_time_idx",indexes)
        self.assertIn("route_rate_event_r159_time_idx",indexes)

    def test_first_five_same_ip_allowed_sixth_rejected(self):
        token="a"*64
        now=1_790_955_000
        self.assertEqual([self.insert(token,now+i) for i in range(5)],[1,1,1,1,1])
        self.assertEqual(self.insert(token,now+5),0)

    def test_hour_window_reopens_after_3600_seconds(self):
        token="b"*64
        now=1_790_955_000
        for i in range(5): self.assertEqual(self.insert(token,now+i),1)
        self.assertEqual(self.insert(token,now+HOUR+5),1)

    def test_daily_cap_is_site_wide_across_ips(self):
        now=1_790_955_000
        for digit in ["1","2","3"]:
            self.assertEqual(self.insert(digit*64,now,daily_limit=3),1)
        self.assertEqual(self.insert("4"*64,now,daily_limit=3),0)

    def test_events_older_than_rolling_day_do_not_count(self):
        now=1_790_955_000
        self.db.execute(
            "INSERT INTO route_rate_event_r159(request_id,ip_token,occurred_at) VALUES(?,?,?)",
            (str(uuid.uuid4()),"5"*64,now-DAY-1),
        )
        self.assertEqual(self.insert("6"*64,now,daily_limit=1),1)

    def test_schema_rejects_non_64_char_token(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "INSERT INTO route_rate_event_r159(request_id,ip_token,occurred_at) VALUES(?,?,?)",
                (str(uuid.uuid4()),"short",1_790_955_000),
            )

    def test_worker_uses_one_atomic_conditional_insert(self):
        source=WORKER.read_text(encoding="utf-8")
        match=re.search(r"const ROUTE_RATE_INSERT_SQL = `(.*?)`;",source,re.S)
        self.assertIsNotNone(match)
        normalized=" ".join(match.group(1).split())
        expected=" ".join(INSERT_SQL.split())
        self.assertEqual(normalized,expected)
        self.assertEqual(normalized.count("COUNT(*)"),2)
        self.assertIn("ON CONFLICT(request_id) DO NOTHING",normalized)

    def test_cleanup_query_is_bounded_to_rolling_day(self):
        source=WORKER.read_text(encoding="utf-8")
        self.assertEqual(
            source.count('DELETE FROM route_rate_event_r159 WHERE occurred_at < ?'),
            1,
        )
        now=1_790_955_000
        self.db.execute(
            "INSERT INTO route_rate_event_r159(request_id,ip_token,occurred_at) VALUES(?,?,?)",
            (str(uuid.uuid4()),"7"*64,now-DAY-1),
        )
        self.db.execute(
            "INSERT INTO route_rate_event_r159(request_id,ip_token,occurred_at) VALUES(?,?,?)",
            (str(uuid.uuid4()),"8"*64,now-1),
        )
        deleted=self.db.execute(
            "DELETE FROM route_rate_event_r159 WHERE occurred_at < ?",
            (now-DAY,),
        ).rowcount
        self.assertEqual(deleted,1)
        self.assertEqual(self.db.execute("SELECT count(*) FROM route_rate_event_r159").fetchone()[0],1)

    def test_no_raw_ip_or_user_input_columns(self):
        sql=SCHEMA.read_text(encoding="utf-8").lower()
        for forbidden in ["goal","answer","locale","audience","raw_ip","ip_address","contact","name"]:
            self.assertNotIn(forbidden,sql)

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(RouteRateSchemaTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    status="PASS" if result.wasSuccessful() else "FAIL"
    print(f"ROUTE_RATE_SCHEMA_{status} tests={result.testsRun} database=:memory: remote_connections=0 hourly_limit=5 daily_limit=env_bound")
    raise SystemExit(0 if result.wasSuccessful() else 1)
