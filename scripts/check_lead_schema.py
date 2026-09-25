#!/usr/bin/env python3
"""Verify the captured D1 schema offline; never connect to a live database."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
from pathlib import Path
import re
import sqlite3
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / 'schema/lead_intake_r101b.sql'
SCHEMA_SHA256 = '8d0c8f0f18c63a36b2602c7c323dda985860230ac9b7bc536c541ea347213e44'
RECEIVER = ROOT / 'services/lead-receiver-cloudflare/src/index.js'
COLUMNS = (
    'request_id', 'received_at', 'expires_at', 'schema', 'name', 'audience',
    'contact', 'goal', 'program', 'locale', 'privacy_consent',
    'adult_confirmed', 'source', 'source_path',
)
REQUEST_ID = '00000000-0000-4000-8000-000000000001'


def iso(value: datetime) -> str:
    return value.isoformat(timespec='milliseconds').replace('+00:00', 'Z')


class SchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.db = sqlite3.connect(':memory:')
        self.addCleanup(self.db.close)
        self.db.executescript(SCHEMA.read_text(encoding='utf-8'))
        source = RECEIVER.read_text(encoding='utf-8')
        pattern = (r'INSERT INTO lead_intake_r101b\s*\((.*?)\)\s*'
                   r'VALUES\s*\((.*?)\)\s*ON CONFLICT\(request_id\) DO NOTHING')
        matches = list(re.finditer(pattern, source, re.S))
        self.assertEqual(len(matches), 1, 'receiver INSERT must be unambiguous')
        match = matches[0]
        self.insert_sql = match.group(0)
        self.assertEqual(tuple(x.strip() for x in match.group(1).split(',')), COLUMNS)
        self.assertEqual([x.strip() for x in match.group(2).split(',')], ['?'] * 14)
        now = datetime.now(timezone.utc)
        self.row = dict(zip(COLUMNS, (
            REQUEST_ID, iso(now), iso(now + timedelta(days=30)),
            'ai-skill-lab.lead.v2', 'Synthetic Adult', 'adult',
            'test@example.invalid', '', '', 'en', 1, 0, 'ai-skill-lab', '/start',
        )))

    def insert(self, **changes: object) -> sqlite3.Cursor:
        row = {**self.row, **changes}
        return self.db.execute(self.insert_sql, tuple(row[key] for key in COLUMNS))

    def test_snapshot_fingerprint(self) -> None:
        self.assertEqual(hashlib.sha256(SCHEMA.read_bytes()).hexdigest(), SCHEMA_SHA256)

    def test_columns_and_implicit_index(self) -> None:
        columns = self.db.execute('PRAGMA table_info(lead_intake_r101b)').fetchall()
        self.assertEqual(tuple(col[1] for col in columns), COLUMNS)
        self.assertEqual([col[1] for col in columns if col[5]], ['request_id'])
        self.assertEqual([col[1] for col in columns if not col[3]], ['source_path'])
        indexes = self.db.execute('PRAGMA index_list(lead_intake_r101b)').fetchall()
        self.assertEqual([(x[1], x[2], x[3]) for x in indexes],
                         [('sqlite_autoindex_lead_intake_r101b_1', 1, 'pk')])

    def test_receiver_insert_and_deduplication(self) -> None:
        self.assertEqual(self.insert().rowcount, 1)
        self.assertEqual(self.insert().rowcount, 0)
        count = self.db.execute('SELECT count(*) FROM lead_intake_r101b').fetchone()[0]
        self.assertEqual(count, 1)

    def test_not_null_constraints(self) -> None:
        for key in COLUMNS:
            if key == 'source_path':
                continue
            with self.subTest(column=key):
                with self.assertRaises(sqlite3.IntegrityError):
                    self.insert(**{key: None})

    def test_optional_source_path(self) -> None:
        self.assertEqual(self.insert(source_path=None).rowcount, 1)

    def test_invalid_domain_values(self) -> None:
        invalid = {'schema': 'other', 'audience': 'unknown', 'locale': 'fr',
                   'privacy_consent': 0, 'adult_confirmed': 2, 'source': 'other'}
        for key, value in invalid.items():
            with self.subTest(column=key):
                with self.assertRaises(sqlite3.IntegrityError):
                    self.insert(**{key: value})

    def test_character_length_boundaries(self) -> None:
        for key, limit in [('name', 80), ('contact', 120), ('goal', 600),
                           ('program', 80), ('source_path', 180)]:
            with self.subTest(column=key):
                self.assertEqual(self.insert(**{key: 'x' * limit}).rowcount, 1)
                self.db.execute('DELETE FROM lead_intake_r101b')
                with self.assertRaises(sqlite3.IntegrityError):
                    self.insert(**{key: 'x' * (limit + 1)})
        for key in ['name', 'contact']:
            with self.subTest(empty_column=key):
                with self.assertRaises(sqlite3.IntegrityError):
                    self.insert(**{key: ''})

    def test_sql_character_limit_is_not_byte_limit(self) -> None:
        goal = '\u044f' * 600
        self.assertGreater(len(goal.encode('utf-8')), 600)
        self.assertEqual(self.insert(goal=goal).rowcount, 1)

    def test_expiry_order(self) -> None:
        for expires in [self.row['received_at'], '2000-01-01T00:00:00.000Z']:
            with self.subTest(expires_at=expires):
                with self.assertRaises(sqlite3.IntegrityError):
                    self.insert(expires_at=expires)

    def test_receiver_cleanup_query(self) -> None:
        source = RECEIVER.read_text(encoding='utf-8')
        matches = re.findall(r'prepare\("(DELETE FROM lead_intake_r101b[^"\n]+)"\)', source)
        self.assertEqual(matches, ['DELETE FROM lead_intake_r101b WHERE expires_at <= ?'])
        self.insert()
        self.insert(request_id='00000000-0000-4000-8000-000000000002',
                    received_at='2000-01-01T00:00:00.000Z',
                    expires_at='2000-02-01T00:00:00.000Z')
        self.assertEqual(self.db.execute(matches[0], (self.row['received_at'],)).rowcount, 1)
        self.assertEqual(self.db.execute(matches[0], (self.row['expires_at'],)).rowcount, 1)

    def test_inbox_selects_match_schema(self) -> None:
        spec = importlib.util.spec_from_file_location('lead_inbox_schema_test',
                                                     ROOT / 'scripts/lead_inbox.py')
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        inbox = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(inbox)
        self.insert()
        cursor = self.db.execute(inbox.build_list_sql(20, 168))
        names = [item[0] for item in cursor.description]
        self.assertFalse({'name', 'contact', 'goal'} & set(names))
        self.assertEqual(len(cursor.fetchall()), 1)
        cursor = self.db.execute(inbox.build_show_sql(REQUEST_ID))
        self.assertEqual(tuple(item[0] for item in cursor.description), COLUMNS)
        self.assertEqual(len(cursor.fetchall()), 1)

    def test_gate_is_wired_once(self) -> None:
        workflow = (ROOT / '.github/workflows/static-qa.yml').read_text(encoding='utf-8')
        preflight = (ROOT / 'scripts/preflight_release.py').read_text(encoding='utf-8')
        self.assertEqual(workflow.count('python scripts/check_lead_schema.py'), 1)
        self.assertEqual(preflight.count('["python", "scripts/check_lead_schema.py"]'), 1)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SchemaTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    status = 'PASS' if result.wasSuccessful() else 'FAIL'
    print(f'LEAD_SCHEMA_OFFLINE_{status} tests={result.testsRun} '
          'database=:memory: remote_connections=0')
    raise SystemExit(0 if result.wasSuccessful() else 1)
