#!/usr/bin/env python3
"""R5 acceptance: immutable R3, exact report copy and local browser only."""
from __future__ import annotations
import argparse
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import phuket_agency_release_profile as profile
import build_phuket_agency_release_r5 as builder
import prepare_phuket_agency_terms_r4 as terms


class R5Acceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = {p.relative_to(profile.LIVE).as_posix(): p.read_bytes()
                     for p in profile.LIVE.rglob('*') if p.is_file()}
        cls.r3 = terms.r3_payload()

    def test_identity_lineage_and_reproduction(self):
        result = profile.verify_integrity()
        self.assertEqual((result['files'], result['routes'], result['r3_files_unchanged']), (104, 56, 101))
        self.assertEqual(builder.render(), self.files)
        self.assertEqual({n for n in self.r3 if self.r3[n] != self.files[n]}, profile.CHANGED_FILES | {'_release.json'})
        self.assertEqual(self.r3['vercel.json'], self.files['vercel.json'])
        self.assertEqual(self.r3['lab-command.js'], self.files['lab-command.js'])

    def test_report_copy_exact_and_not_a_legal_approval(self):
        data = terms.copy_data()
        self.assertEqual(data['source']['sha256'], profile.REPORT_SHA)
        self.assertFalse(any(data['authority'].values()))
        for locale, route in terms.ROUTES.items():
            name = route.lstrip('/') + '.html'
            self.assertEqual(terms.add_terms(self.r3[name].decode('utf-8'), locale).encode('utf-8'), self.files[name])
            self.assertEqual(self.files[name].count(b'id="agency-pilot-terms"'), 1)
            with self.assertRaises(ValueError):
                terms.add_terms(self.files[name].decode('utf-8'), locale)

    def test_payload_change_fails(self):
        target = profile.LIVE / 'phuket-universe.html'
        read = Path.read_bytes
        def changed(path):
            raw = read(path)
            return raw + b'changed' if path == target else raw
        with patch.object(Path, 'read_bytes', changed), self.assertRaisesRegex(ValueError, 'payload differs'):
            profile.verify_integrity()

    def test_manifest_duplicates_fail(self):
        original = json.loads(self.files['_release.json'])
        original['files'][1] = original['files'][0]
        target = profile.LIVE / '_release.json'
        read = Path.read_text
        def changed(path, *a, **kw):
            return json.dumps(original) if path == target else read(path, *a, **kw)
        with patch.object(Path, 'read_text', changed), self.assertRaisesRegex(ValueError, 'duplicate/missing'):
            profile.verify_integrity()

    def test_authority_budget_and_provenance_changes_fail(self):
        original = profile.profile()
        variants = []
        p = copy.deepcopy(original); p['authority']['deploy'] = True; variants.append(p)
        p = copy.deepcopy(original); p['budgets']['payload_max_bytes'] += 1; variants.append(p)
        p = copy.deepcopy(original); p['source_report_sha256'] = '0' * 64; variants.append(p)
        p = copy.deepcopy(original); p['r3_file_pins']['index.html']['sha256'] = '0' * 64; variants.append(p)
        p = copy.deepcopy(original); p['universe_routes'].append('/unauthorized'); variants.append(p)
        p = copy.deepcopy(original); p['transfer_profiles']['phuket-universe.html']['css_br_max'] += 1; variants.append(p)
        read = Path.read_text
        for idx, value in enumerate(variants):
            def changed(path, *a, **kw):
                return json.dumps(value) if path == profile.PROFILE_PATH else read(path, *a, **kw)
            with self.subTest(variant=idx), patch.object(Path, 'read_text', changed), self.assertRaises(ValueError):
                profile.verify_integrity()

    def test_routes_and_shell_fail_closed(self):
        import guide_route_admission as admission
        import phuket_release_profile as base
        self.assertEqual(admission.admitted_route_count(), 56)
        self.assertEqual(admission.require_public_html(profile.LIVE), 56)
        with self.assertRaises(ValueError):
            admission.require_route_set(admission.admitted_routes() | {'/unauthorized'})
        self.assertTrue(base.universe_page(profile.LIVE / 'phuket-universe.html'))
        self.assertFalse(base.universe_page(profile.LIVE / 'business.html'))


def run_units() -> None:
    result = unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(R5Acceptance))
    if not result.wasSuccessful():
        raise ValueError('R5 targeted acceptance failed')


def browser_acceptance() -> list[dict]:
    import mimetypes
    import psutil
    from urllib.parse import urlsplit, unquote
    from playwright.sync_api import sync_playwright
    if psutil.virtual_memory().available < 2 * 1024**3:
        raise RuntimeError('Inherited host-memory floor not met')
    files = {p.relative_to(profile.LIVE).as_posix(): p.read_bytes() for p in profile.LIVE.rglob('*') if p.is_file()}
    profile.verify_integrity()
    data = terms.copy_data()
    cfg = json.loads(files['vercel.json'])
    headers = {h['key']: h['value'] for rule in cfg['headers'] if rule['source'] == '/(.*)' for h in rule['headers']}
    exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=exe, headless=True, timeout=20000,
            args=['--disable-background-networking', '--disable-component-update', '--no-first-run'])
        try:
            for locale, path in terms.ROUTES.items():
                for enabled in (False, True):
                    for width in (390, 1440):
                        ctx = browser.new_context(java_script_enabled=enabled, offline=True, service_workers='block',
                                                  viewport={'width': width, 'height': 844})
                        ctx.set_default_timeout(6000)
                        page = ctx.new_page()
                        denied, errors, events = [], [], []
                        page.on('pageerror', lambda e: errors.append(str(e)))
                        def fulfill(rt):
                            req = rt.request; u = urlsplit(req.url)
                            if u.scheme != 'https' or u.netloc != 'aiskillab.work':
                                denied.append(req.url); rt.abort(); return
                            if u.path == '/api/event' and req.method == 'POST':
                                events.append(json.loads(req.post_data or '{}'))
                                rt.fulfill(status=200, body='{"ok":true}', headers={'Content-Type': 'application/json'}); return
                            if req.method != 'GET' or u.query:
                                denied.append(req.url); rt.abort(); return
                            if u.path == '/_vercel/insights/script.js':
                                rt.fulfill(status=200, body='/* no telemetry in local acceptance */', headers={'Content-Type': 'application/javascript'}); return
                            name = unquote(u.path).lstrip('/')
                            if name not in files: name += '.html'
                            if name not in files or '..' in Path(name).parts:
                                denied.append(req.url); rt.abort(); return
                            mime = {'.css': 'text/css', '.js': 'application/javascript', '.html': 'text/html; charset=utf-8', '.woff2': 'font/woff2'}.get(Path(name).suffix)
                            rt.fulfill(status=200, body=files[name], headers={**headers, 'Content-Type': mime or mimetypes.guess_type(name)[0] or 'application/octet-stream'})
                        ctx.route('**/*', fulfill)
                        response = page.goto('https://aiskillab.work' + path, wait_until='load', timeout=15000)
                        page.evaluate('document.fonts.ready')
                        assert response is not None and response.status == 200
                        closed_height = page.evaluate('document.documentElement.scrollHeight')
                        details = page.locator('#agency-pilot-terms')
                        assert details.count() == 1 and details.get_attribute('open') is None
                        assert details.locator('p').all_text_contents() == data[locale]['paragraphs']
                        details.locator('summary').click()
                        assert details.get_attribute('open') is not None and details.locator('p').first.is_visible()
                        assert page.locator('h1').count() == 1 and page.locator('.pu-page svg').count() == 8
                        assert page.locator('[style],style').count() == 0 and page.locator('form').count() == 0
                        assert page.evaluate('document.documentElement.scrollWidth') <= width + 1
                        open_height = page.evaluate('document.documentElement.scrollHeight')
                        if enabled:
                            page.evaluate("""() => {
                                for (const href of ['https://cal.com/fixture','https://t.me/fixture','https://wa.me/1000','https://line.me/fixture','mailto:test@example.invalid']) {
                                    const a=document.createElement('a');a.href=href;a.addEventListener('click',e=>e.preventDefault());document.body.appendChild(a);a.click();a.remove();
                                }
                                for (const event of ['lead_submit_ok','lead_submit_error']) dispatchEvent(new CustomEvent('asl:lead-event',{detail:{event}}));
                            }""")
                            page.wait_for_timeout(100)
                            assert events == [{'event':e,'page':path,'locale':locale} for e in ['cal_click','telegram_click','whatsapp_click','line_click','email_click','lead_submit_ok','lead_submit_error']]
                        else:
                            assert not events
                        details.locator('summary').click()
                        assert details.get_attribute('open') is None
                        assert not errors and not denied, repr((errors, denied))
                        result = {'locale':locale, 'js':enabled, 'width':width, 'height_closed':closed_height,
                                  'height_open':open_height, 'report_paragraphs':3, 'events_mocked':len(events), 'real_api_requests':0}
                        results.append(result); print('R5_BROWSER_PASS', json.dumps(result), flush=True)
                        ctx.close()
        finally:
            browser.close()
    return results


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(); ap.add_argument('--browser', action='store_true'); args = ap.parse_args()
    run_units()
    if args.browser:
        print('R5_BROWSER_CASES', len(browser_acceptance()))
    print('R5_TARGETED_ACCEPTANCE_PASS_LOCAL_ONLY')
