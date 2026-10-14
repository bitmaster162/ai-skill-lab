#!/usr/bin/env python3
"""R6 item acceptance: empty inventory, exact lineage, Next and static parity."""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
import build_phuket_housing_release_r6 as builder
import phuket_housing_release_profile as profile


class R6Acceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = {p.relative_to(profile.LIVE).as_posix(): p.read_bytes() for p in profile.LIVE.rglob('*') if p.is_file()}
        cls.parent = builder.preview.parent_payload()

    def test_exact_lineage_and_reproduction(self):
        result = profile.verify_integrity()
        self.assertEqual((result['files'], result['routes'], result['r5_files_unchanged']), (106, 56, 102))
        self.assertEqual(builder.render(), self.files)
        self.assertEqual({n for n in self.parent if self.files[n] != self.parent[n]}, profile.PAGES | {'_release.json'})
        self.assertEqual(self.files['vercel.json'], self.parent['vercel.json'])
        self.assertEqual(self.files['lab-command.js'], self.parent['lab-command.js'])
        self.assertEqual(self.files['phuket-universe.css'], self.parent['phuket-universe.css'])

    def test_no_real_inventory_or_policy_authority(self):
        values, consent = builder.inputs()
        self.assertEqual(values, [list(builder.catalog.HEADERS)])
        self.assertEqual(consent['agencies'], [])
        self.assertIsNone(consent['max_listing_age_days'])
        self.assertFalse(any(profile.profile()['authority'].values()))
        read = Path.read_bytes
        for changed in [dict(json.loads(builder.SNAPSHOT.read_bytes()), values=values + [['unapproved']]),
                        dict(json.loads(builder.SNAPSHOT.read_bytes()), as_of='2026-10-15')]:
            def override(p):
                return json.dumps(changed).encode() if p == builder.SNAPSHOT else read(p)
            with patch.object(Path, 'read_bytes', override), self.assertRaises(ValueError):
                builder.inputs()

    def test_payload_tamper_fails(self):
        read = Path.read_bytes
        target = profile.LIVE / 'phuket-housing-u2.js'
        def override(p):
            raw = read(p)
            return raw + b'tamper' if p == target else raw
        with patch.object(Path, 'read_bytes', override), self.assertRaisesRegex(ValueError, 'payload differs'):
            profile.verify_integrity()

    def test_duplicate_manifest_rejected(self):
        m = json.loads(self.files['_release.json']); m['files'][1] = m['files'][0]
        read = Path.read_text
        def override(p, *args, **kw):
            return json.dumps(m) if p == profile.LIVE / '_release.json' else read(p, *args, **kw)
        with patch.object(Path, 'read_text', override), self.assertRaisesRegex(ValueError, 'duplicate/missing'):
            profile.verify_integrity()

    def test_authority_budgets_and_parent_mutations_fail(self):
        good = profile.profile(); variants = []
        p = copy.deepcopy(good); p['authority']['real_listings'] = True; variants.append(p)
        p = copy.deepcopy(good); p['authority']['scheduler'] = True; variants.append(p)
        p = copy.deepcopy(good); p['budgets']['payload_max_bytes'] += 1; variants.append(p)
        p = copy.deepcopy(good); p['input_sha256'] = '0' * 64; variants.append(p)
        p = copy.deepcopy(good); p['r5_file_pins']['index.html']['sha256'] = '0' * 64; variants.append(p)
        p = copy.deepcopy(good); p['transfer_profiles']['phuket-universe.html']['first_br_max'] += 1; variants.append(p)
        read = Path.read_text
        for item in variants:
            def override(path, *args, **kw):
                return json.dumps(item) if path == profile.PROFILE_PATH else read(path, *args, **kw)
            with self.subTest(mutation=variants.index(item)), patch.object(Path, 'read_text', override), self.assertRaises(ValueError):
                profile.verify_integrity()

    def test_only_housing_section_changes_and_terms_preserved(self):
        import phuket_release_profile as shared
        for name in profile.PAGES:
            old = self.parent[name].decode('utf-8'); new = self.files[name].decode('utf-8')
            a, b = builder.preview.section_bounds(old); c, d = builder.preview.section_bounds(new)
            # Document resource tags are the only changes outside homes.
            stripped = new.replace('<link rel="stylesheet" href="/phuket-housing-u2.css">', '')
            stripped = stripped.replace('<script src="/phuket-housing-u2.js" defer></script>', '')
            c, d = builder.preview.section_bounds(stripped)
            self.assertEqual(old[:a], stripped[:c]); self.assertEqual(old[b:], stripped[d:])
            self.assertTrue(shared.universe_page(profile.LIVE / name))
            self.assertNotIn('data-u2-card', new); self.assertNotIn('class="pu-s083"', new)
            self.assertEqual(new.count('id="agency-pilot-terms"'), 1)
            self.assertEqual(new.count('<svg'), 7)
            self.assertNotIn('<form', new)
            self.assertIn('<noscript>', new)

    def test_generated_sources_and_private_data_boundary(self):
        for path, data in builder.generated_sources().items():
            self.assertEqual(path.read_bytes(), data)
        for name in ['phuket-universe.html', 'en/phuket-universe.html', 'phuket-housing-u2.js']:
            raw = self.files[name].decode('utf-8')
            for key in ['evidence_sha256', 'valid_through', 'max_listing_age_days', 'consent_registry', 'Synthetic Agency']:
                self.assertNotIn(key, raw)
        self.assertNotIn('fetch(', builder.client_script().decode('utf-8'))
        self.assertIn("document.addEventListener('phuket-housing:ready'", builder.client_script().decode('utf-8'))

    def test_route_scope_is_not_relaxed(self):
        import guide_route_admission as admission
        self.assertEqual(admission.admitted_route_count(), 56)
        self.assertEqual(admission.require_public_html(profile.LIVE), 56)
        with self.assertRaises(ValueError):
            admission.require_route_set(admission.admitted_routes() | {'/not-reviewed'})


def run_units() -> None:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(R6Acceptance)
    # Reuse the actual importer negative tests; no qualification-package expansion.
    import test_catalog
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(test_catalog.CatalogTests))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():
        raise ValueError('R6 item acceptance failed')


def next_parity() -> None:
    sections = builder.section_sources()
    seen = set()
    for path in (profile.ROOT / '.next/server/app').rglob('*.html'):
        text = path.read_text(encoding='utf-8')
        if 'data-u2-catalog' not in text:
            continue
        locale = 'en' if '<html lang="en"' in text else 'ru'
        if sections[locale] not in text or text.count('id="agency-pilot-terms"') != 1:
            raise ValueError('R6 Next/static compiled section parity failed')
        seen.add(locale)
    if seen != {'ru', 'en'}:
        raise ValueError('R6 Next both locales must be built')
    print('R6_NEXT_STATIC_PARITY_PASS locales=2')


def browser_acceptance() -> None:
    import test_browser
    original = test_browser.render
    def current_render(values, policy, **kwargs):
        if values == [list(builder.catalog.HEADERS)]:
            return builder.render(), {'fixture': 'exact R6 empty-inventory'}
        # Synthetic nonempty rows never become release inputs or written assets.
        files, metadata = original(values, policy, **kwargs)
        files['phuket-housing-u2.js'] = builder.client_script()
        return files, metadata
    with patch.object(test_browser, 'render', current_render):
        test_browser.main()
    print('R6_BROWSER_PASS exact_empty=8 synthetic=8 real_api_requests=0')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(); ap.add_argument('--browser', action='store_true'); ap.add_argument('--next', action='store_true')
    args = ap.parse_args()
    run_units()
    if args.browser: browser_acceptance()
    if args.next: next_parity()
    print('R6_TARGETED_PASS_LOCAL_ONLY')
