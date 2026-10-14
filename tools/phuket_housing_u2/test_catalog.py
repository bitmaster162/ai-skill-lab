"""U2 item acceptance. All nonempty inventory and consents here are synthetic."""
from __future__ import annotations
import copy
import csv
import io
import json
import unittest
from html.parser import HTMLParser
from catalog import HEADERS, TERMS_SHA, canonical, compile_catalog, read_values, sha, https_source
import preview

AS_OF = '2026-10-14'


def policy_fixture() -> dict:
    return {'schema': 'phuket-housing-consents.v1', 'terms_sha256': TERMS_SHA, 'max_listing_age_days': 1,
            'authority': {'publish': False, 'deploy': False, 'legal_review_completed': False},
            'agencies': [{'domain': 'agency.example', 'source_name': 'Synthetic Agency', 'status': 'confirmed',
                          'terms_sha256': TERMS_SHA, 'evidence_sha256': sha(b'synthetic unit-test consent, not a real agency'),
                          'fields': list(HEADERS[:-1]), 'granted_on': '2026-10-01', 'valid_through': '2026-10-31'}]}


def rows_fixture() -> list:
    return [list(HEADERS),
            ['rent', 'Rawai', 'condo', 0, '25000', 'Synthetic studio', 'Synthetic Agency', 'https://agency.example/studio', AS_OF, 'yes'],
            ['rent', 'Bang Tao', 'villa', 4, '60000.50', 'Synthetic villa', 'Synthetic Agency', 'https://agency.example/villa', AS_OF, 'yes'],
            ['sale', 'Rawai', 'house', 3, '4500000', 'Synthetic house', 'Synthetic Agency', 'https://agency.example/house', AS_OF, 'yes']]


def compile_fixture(rows=None, policy=None):
    policy = policy if policy is not None else policy_fixture()
    return compile_catalog(rows if rows is not None else rows_fixture(), policy, policy_sha=sha(canonical(policy)), as_of=AS_OF)


class Tags(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False); self.tags = []; self.feed(source)
    def handle_starttag(self, tag, attrs): self.tags.append((tag, dict(attrs)))


class CatalogTests(unittest.TestCase):
    def test_empty_sheet_and_missing_consents_do_not_invent_inventory(self):
        policy = policy_fixture(); policy['agencies'] = []; policy['max_listing_age_days'] = None
        out = compile_fixture([list(HEADERS)], policy)
        self.assertEqual(out['listings'], [])
        self.assertEqual(out['counts']['accepted'], 0)
        self.assertFalse(out['authority']['publish'])

    def test_source_fields_and_exact_price(self):
        data = compile_fixture()['listings']; self.assertEqual(len(data), 3)
        villa = next(x for x in data if x['type'] == 'villa')
        self.assertEqual(villa['price_minor'], 6000050)
        self.assertEqual(villa['price_period'], 'unspecified')
        self.assertNotIn('evidence_sha256', json.dumps(data))
        self.assertNotIn('granted_on', json.dumps(data))
        self.assertNotIn('partner_ok', json.dumps(data))

    def test_yes_is_required(self):
        for flag in ('no', 'YES', True, '', None):
            rows = rows_fixture()[:2]; rows[1][-1] = flag
            self.assertEqual(compile_fixture(rows)['listings'], [])

    def test_https_domain_and_tracking_boundaries(self):
        urls = ['http://agency.example/a', 'javascript:alert(1)', 'https://agency.example@evil.example/a',
                'https://127.0.0.1/a', 'https://agency.example:8443/a', 'https://localhost/a',
                'https://agency.example/a?token=private', 'https://agency.example/a#fragment',
                'https://agency.example/a%0d%0aInjected', 'https://agency.example\\@evil.example/a',
                'https://sub.agency.example/a', 'https://agency.example/a?contact=a%40b.com']
        for url in urls:
            with self.subTest(url=url):
                rows = rows_fixture()[:2]; rows[1][7] = url
                self.assertEqual(compile_fixture(rows)['listings'], [])
        self.assertEqual(https_source('https://agency.example/property?id=123')[1], 'agency.example')

    def test_consent_flags_are_not_sufficient_without_evidence(self):
        for key, value in [('status', 'revoked'), ('evidence_sha256', ''), ('terms_sha256', '0'*64),
                           ('valid_through', '2026-10-13'), ('granted_on', '2026-10-15'), ('fields', ['title'])]:
            p = policy_fixture(); p['agencies'][0][key] = value
            with self.subTest(key=key): self.assertEqual(compile_fixture(policy=p)['listings'], [])
        p = policy_fixture(); p['max_listing_age_days'] = None
        self.assertIn('freshness_policy_unset', compile_fixture(policy=p)['counts']['excluded'])
        p = policy_fixture(); p['agencies'] = []
        self.assertIn('consent_missing_or_revoked', compile_fixture(policy=p)['counts']['excluded'])

    def test_policy_pin_and_authority_mutations_fail_closed(self):
        p = policy_fixture(); digest = sha(canonical(p)); p['max_listing_age_days'] = 2
        with self.assertRaisesRegex(ValueError, 'policy_digest'):
            compile_catalog(rows_fixture(), p, policy_sha=digest, as_of=AS_OF)
        for flag in ('publish', 'deploy', 'legal_review_completed'):
            p = policy_fixture(); p['authority'][flag] = True
            with self.subTest(flag=flag), self.assertRaisesRegex(ValueError, 'local_authority'):
                compile_fixture(policy=p)
        p = policy_fixture(); p['agencies'].append(copy.deepcopy(p['agencies'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate'): compile_fixture(policy=p)

    def test_dates_and_numbers(self):
        for col, bad in [(8, '2026-10-15'), (8, '2026-10-12'), (8, '14/10/2026'), (8, 46309),
                         (4, -1), (4, 0), (4, 'NaN'), (4, '1e9'), (4, '25,000'), (4, '100.001'),
                         (3, -1), (3, '1.5'), (3, True), (1, 'Unknown district'), (2, 'hotel')]:
            rows = rows_fixture()[:2]; rows[1][col] = bad
            with self.subTest(col=col, value=bad): self.assertEqual(compile_fixture(rows)['listings'], [])

    def test_conflicting_duplicates_quarantine_all_without_order_bias(self):
        rows = rows_fixture()[:2]; rows.append(copy.deepcopy(rows[1]))
        self.assertEqual(len(compile_fixture(rows)['listings']), 1)
        rows[-1][4] = '99999'
        out = compile_fixture(rows)
        self.assertEqual(out['listings'], [])
        self.assertEqual(out, compile_fixture([rows[0], *reversed(rows[1:])]))

    def test_no_cross_agency_property_deduplication(self):
        rows = rows_fixture()[:2]; rows.append(copy.deepcopy(rows[1])); rows[-1][6] = 'Other Synthetic Agency'
        p = policy_fixture(); second = copy.deepcopy(p['agencies'][0]); second['source_name'] = rows[-1][6]; p['agencies'].append(second)
        self.assertEqual(len(compile_fixture(rows, p)['listings']), 2)

    def test_csv_json_and_schema_budgets(self):
        rows = rows_fixture(); raw = json.dumps({'values': rows}).encode()
        self.assertEqual(read_values(raw), rows)
        csvfile = io.StringIO(); writer = csv.writer(csvfile); writer.writerows(rows)
        self.assertEqual(compile_fixture(read_values(csvfile.getvalue().encode(), 'csv')), compile_fixture(rows))
        for bad in (b'[]', json.dumps([['title'], ['x']]).encode(), b'x'*(1024*1024+1)):
            with self.assertRaises(ValueError): read_values(bad)

    def test_text_is_escaped_not_executed_and_preview_preserves_other_sections(self):
        rows = rows_fixture(); rows[1][5] = '<img src=x onerror=alert(1)> & unsafe "title"'
        files, _ = preview.render(rows, policy_fixture(), policy_sha=sha(canonical(policy_fixture())), as_of=AS_OF)
        base = preview.parent_payload()
        for name in ('phuket-universe.html', 'en/phuket-universe.html'):
            source = base[name].decode(); actual = files[name].decode()
            self.assertNotIn('<img src=x', actual)
            self.assertIn('&lt;img src=x', actual)
            start, end = preview.section_bounds(source); a, b = preview.section_bounds(actual)
            self.assertEqual(source[start-100:start], actual[a-100:a])
            self.assertIn(source[end:source.index('</body>')], actual)
            doc = Tags(actual)
            links = [attrs['href'] for tag, attrs in doc.tags if tag == 'a' and attrs.get('href', '').startswith('https://agency.example/')]
            self.assertEqual(len(links), 3)
            self.assertEqual(sum('data-u2-card' in attrs for _, attrs in doc.tags), 3)
            self.assertFalse(any(tag in ('img', 'form', 'style') or 'style' in attrs for tag, attrs in doc.tags))
        self.assertEqual(files['vercel.json'], base['vercel.json'])
        self.assertEqual(files['lab-command.js'], base['lab-command.js'])
        changed = {key for key in base if files[key] != base[key]}
        self.assertEqual(changed, {'_release.json', 'phuket-universe.html', 'en/phuket-universe.html'})

    def test_determinism_and_placeholder_removal(self):
        args = {'policy_sha': sha(canonical(policy_fixture())), 'as_of': AS_OF}
        a, receipt = preview.render(rows_fixture(), policy_fixture(), **args)
        b, _ = preview.render(rows_fixture(), policy_fixture(), **args)
        self.assertEqual(a, b); self.assertFalse(receipt['authority']['publish'])
        empty, _ = preview.render([list(HEADERS)], policy_fixture(), **args)
        self.assertIn('Скоро: агентства добавляют объекты', empty['phuket-universe.html'].decode())
        self.assertNotIn('[Цена]', empty['phuket-universe.html'].decode())
        self.assertNotIn('Synthetic', empty['phuket-universe.html'].decode())


if __name__ == '__main__': unittest.main(verbosity=2)
