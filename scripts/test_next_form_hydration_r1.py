#!/usr/bin/env python3
"""Test a locally built Next renderer. All browser requests are intercepted offline.

Requires a completed locked Next build with NEXT_PUBLIC_LEAD_FORM_ENABLED=true.
No HTTP server, production calls, real leads, browser profiles or deployments.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import mimetypes
from pathlib import Path
import time
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://aiskillab.work'
CASES = ('ssr_nojs', 'bundle_missing', 'healthy_click', 'healthy_enter',
         'no_fetch', 'formdata_missing', 'from_entries_polyfilled', 'from_entries_blocked', 'response_false',
         'response_string', 'http_failure', 'json_bad', 'network_failure',
         'double_submit', 'privacy_missing', 'youth_parent', 'youth_teen')
FAULTS = {'ssr_nojs', 'bundle_missing', 'no_fetch', 'formdata_missing', 'from_entries_blocked'}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


class Head(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = ''; self.canonical = ''; self.h1 = 0
        self.title = ''; self.in_title = False; self.description = ''
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html': self.lang = a.get('lang', '')
        if tag == 'h1': self.h1 += 1
        if tag == 'title': self.in_title = True
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical = a.get('href', '')
        if tag == 'meta' and a.get('name') == 'description': self.description = a.get('content', '')
    def handle_endtag(self, tag):
        if tag == 'title': self.in_title = False
    def handle_data(self, value):
        if self.in_title: self.title += value


def inspect_build() -> tuple[dict, dict]:
    build = ROOT / '.next/server/app'
    require((ROOT / '.next/BUILD_ID').is_file(), 'Completed Next build missing')
    routes = {}; details = {}
    expected = {urlsplit(x.text).path for x in ET.parse(ROOT / 'deploy/live/sitemap.xml').getroot().findall('{*}url/{*}loc')}
    for path in build.rglob('*.html'):
        parser = Head(); parser.feed(path.read_text(encoding='utf-8'))
        if not parser.canonical or urlsplit(parser.canonical).netloc != 'aiskillab.work': continue
        route = urlsplit(parser.canonical).path.rstrip('/') or '/'
        require(route not in routes, 'Duplicate Next canonical route: ' + route)
        require(parser.lang == ('en' if route == '/en' or route.startswith('/en/') else 'ru'), 'Next language mismatch: ' + route)
        require(parser.h1 == 1, 'Next H1 count mismatch: ' + route)
        routes[route] = path
        details[route] = {'lang': parser.lang, 'title': parser.title, 'description': parser.description,
                          'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    require(set(routes) == expected and len(routes) == 54, 'Next route set mismatch')
    require(details['/en']['title'] == 'AI Skill Lab \u00b7 Phuket \u2014 AI learning and workflow pilots', 'Next English home title')
    require(details['/en/start']['title'] == 'Start \u2014 pick a track and first task | AI Skill Lab \u00b7 Phuket', 'Next start title')
    require(len(details['/en/guides/ai-safety-for-kids']['description']) == 150, 'Next guide description')
    return routes, {'routes': 54, 'locale_count': {'ru': 27, 'en': 27}, 'h1_passed': 54,
                    'metadata_targets': {r: details[r] for r in ('/en', '/en/start', '/en/guides/ai-safety-for-kids')},
                    'build_id': (ROOT / '.next/BUILD_ID').read_text(encoding='utf-8').strip()}


def run(chrome: str, report: dict) -> None:
    import psutil
    from playwright.sync_api import sync_playwright
    require(psutil.virtual_memory().available >= 2*1024**3, 'HOST_MEMORY_HOLD: 2 GiB required before launch')
    routes, metadata = inspect_build(); report['next_routes'] = metadata
    report.update(cases=[], continued_requests=0, real_lead_requests=0, user_profile_used=False,
                  runtime_scope='Actual compiled Next HTML and chunks; all requests mocked/fulfilled/aborted',
                  static_production_csp_test=False)
    started = time.monotonic()
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=chrome, headless=True, timeout=15000,
                                   args=['--disable-background-networking', '--disable-component-update', '--no-first-run'])
        report['browser'] = browser.version
        try:
            for locale in ('ru', 'en'):
                path = '/start' if locale == 'ru' else '/en/start'
                for width in (1440, 390):
                    for scenario in CASES:
                        require(time.monotonic()-started < 160, 'Browser wall-time budget reached')
                        ctx = browser.new_context(java_script_enabled=scenario != 'ssr_nojs',
                              service_workers='block', offline=True, viewport={'width': width, 'height': 900})
                        ctx.set_default_timeout(6000)
                        calls = []; native_attempts = []; errors = []; assets = []; events = []
                        if scenario == 'no_fetch': ctx.add_init_script('window.fetch = undefined;')
                        if scenario == 'formdata_missing': ctx.add_init_script('window.FormData = undefined;')
                        if scenario == 'from_entries_polyfilled': ctx.add_init_script('Object.fromEntries = undefined;')
                        if scenario == 'from_entries_blocked': ctx.add_init_script("Object.defineProperty(Object,'fromEntries',{value:undefined,writable:false,configurable:false});")
                        def intercept(rt):
                            req = rt.request; u = urlsplit(req.url)
                            if u.netloc != 'aiskillab.work': rt.abort(); return
                            if req.method == 'POST' and u.path == '/api/lead':
                                payload = req.post_data or ''
                                require(len(payload) < 4096 and 'ASL_SYNTHETIC' in payload, 'Unexpected POST body')
                                calls.append(json.loads(payload))
                                if scenario == 'network_failure': rt.abort(); return
                                if scenario == 'json_bad': rt.fulfill(status=200, body='not-json', content_type='application/json'); return
                                value = {'ok': False} if scenario in ('response_false', 'http_failure') else {'ok': 'yes'} if scenario == 'response_string' else {'ok': True}
                                rt.fulfill(status=503 if scenario == 'http_failure' else 200,
                                           body=json.dumps(value), content_type='application/json'); return
                            if req.method == 'POST' and u.path == '/api/event':
                                event = json.loads(req.post_data or '{}')
                                require(set(event) == {'event', 'page', 'locale'}, 'Event included unexpected fields')
                                require(event['event'] in ('lead_submit_ok','lead_submit_error') and event['page'] == path and event['locale'] == locale, 'Unexpected public event')
                                events.append(event)
                                rt.fulfill(status=200, body='{"ok":true}', content_type='application/json'); return
                            if req.method != 'GET' or 'ASL_SYNTHETIC' in unquote(req.url):
                                native_attempts.append({'method': req.method, 'path': u.path}); rt.abort(); return
                            if u.path.startswith('/api/') or u.path.startswith('/_vercel/') or u.query:
                                rt.abort(); return
                            dest = None
                            if u.path in routes and req.resource_type == 'document': dest = routes[u.path]
                            elif u.path.startswith('/_next/static/'):
                                if scenario == 'bundle_missing' and u.path.endswith('.js'): rt.abort(); return
                                dest = ROOT / '.next/static' / u.path.removeprefix('/_next/static/')
                            else: dest = ROOT / 'public' / u.path.lstrip('/')
                            dest = dest.resolve()
                            if not dest.is_relative_to(ROOT) or not dest.is_file(): rt.abort(); return
                            ctype = 'application/javascript' if dest.suffix == '.js' else mimetypes.guess_type(dest.name)[0] or 'application/octet-stream'
                            assets.append(dest.relative_to(ROOT).as_posix())
                            rt.fulfill(status=200, body=dest.read_bytes(), content_type=ctype)
                        ctx.route('**/*', intercept)
                        page = ctx.new_page(); page.on('pageerror', lambda err: errors.append(str(err)[:500]))
                        row = {'locale': locale, 'width': width, 'scenario': scenario, 'status': 'RUNNING'}
                        report['cases'].append(row)
                        try:
                            page.goto(ORIGIN+path, wait_until='load', timeout=10000)
                            form = page.locator('form.leadForm'); require(form.count() == 1, 'Next form missing or duplicate')
                            submit = form.locator('button[type="submit"]'); note = form.locator('[data-lead-readiness]')
                            direct = form.locator('[data-lead-direct-contact] a')
                            require(direct.is_visible(), 'Direct contact fallback missing')
                            if scenario in FAULTS:
                                page.wait_for_timeout(200)
                                row['observed_capabilities'] = page.evaluate("() => ({fetch:typeof window.fetch,formData:typeof window.FormData,fromEntries:typeof Object.fromEntries})")
                                require(submit.is_disabled() and note.is_visible(), 'Next failure mode is not safely unavailable')
                                require(form.get_attribute('data-lead-state') == 'unready', 'Next failure flag')
                                form.locator('[name="name"]').fill('ASL_SYNTHETIC_NEXT')
                                form.locator('[name="contact"]').fill('asl-synthetic@example.invalid')
                                form.locator('[name="privacyConsent"]').check()
                                form.locator('[name="contact"]').press('Enter', no_wait_after=True)
                                page.wait_for_timeout(75)
                                require(not calls and not native_attempts and page.url == ORIGIN+path, 'Unavailable form attempted transmission')
                            else:
                                page.locator('form.leadForm[data-lead-state="ready"]').wait_for(state='attached')
                                require(not note.is_visible() and submit.is_enabled(), 'Next hydration not ready')
                                require(not errors, 'Next runtime page error: ' + repr(errors))
                                form.locator('[name="name"]').fill('ASL_SYNTHETIC_NEXT')
                                form.locator('[name="contact"]').fill('asl-synthetic@example.invalid')
                                form.locator('[name="goal"]').fill('ASL_SYNTHETIC_NO_LIVE_REQUEST')
                                if scenario != 'privacy_missing': form.locator('[name="privacyConsent"]').check()
                                if scenario.startswith('youth_'):
                                    audience = 'parent' if scenario == 'youth_parent' else 'teen'
                                    form.locator('[name="audience"]').select_option(audience)
                                    adult = form.locator('[name="adultConfirmation"]'); adult.wait_for(state='visible')
                                    require(adult.get_attribute('required') is not None, 'Adult confirmation not required')
                                    submit.click(); page.wait_for_timeout(75)
                                    require(not calls, 'Youth submit without confirmation')
                                    adult.check()
                                if scenario == 'double_submit':
                                    form.evaluate("f => { f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})); f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})); }")
                                elif scenario == 'healthy_enter': form.locator('[name="contact"]').press('Enter', no_wait_after=True)
                                else: submit.click()
                                if scenario == 'privacy_missing':
                                    page.wait_for_timeout(100); require(not calls, 'Privacy validation bypass')
                                else:
                                    success = scenario in ('healthy_click','healthy_enter','from_entries_polyfilled','double_submit','youth_parent','youth_teen')
                                    form.locator('.formMessage.success' if success else '.formMessage.error').wait_for(state='visible')
                                    require(len(calls) == 1 and calls[0].get('locale') == locale, 'Wrong request count or locale')
                                    require(calls[0].get('privacyConsent') == 'yes', 'Consent absent')
                                    if scenario.startswith('youth_'): require(calls[0].get('adultConfirmation') == 'yes', 'Adult flag absent')
                                    require(submit.is_enabled(), 'Button remains disabled after response')
                                    require(form.locator('[name="name"]').input_value() == ('' if success else 'ASL_SYNTHETIC_NEXT'), 'Unexpected data reset')
                                require(not native_attempts and page.url == ORIGIN+path, 'Native data transmission')
                            row.update(status='PASS', mocked_posts=len(calls), native_attempts=len(native_attempts),
                                       fulfilled_asset_count=len(assets), mocked_events=len(events), ready=form.get_attribute('data-lead-state'))
                            print(json.dumps({'case': len(report['cases']), **row}, ensure_ascii=True), flush=True)
                        except Exception as exc:
                            row.update(status='FAIL', error=str(exc), page_errors=errors, native_attempts=native_attempts, mocked_posts=len(calls), mocked_events=events); raise
                        finally: ctx.close()
        finally: browser.close()
    report.update(passed=sum(x['status']=='PASS' for x in report['cases']), count=len(report['cases']), seconds=round(time.monotonic()-started,2))
    require(report['count'] == report['passed'] == 68, 'Incomplete hydration suite')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--chrome', required=True); ap.add_argument('--receipt', required=True, type=Path)
    args = ap.parse_args(); require(not args.receipt.exists(), 'Receipt already exists')
    result = {'schema':'ai-skill-lab.next-form-hydration.v1', 'status':'HOLD'}
    try:
        run(args.chrome, result); result['status'] = 'PASS_LOCAL_ONLY'
    except Exception as exc:
        result['error'] = str(exc); raise
    finally:
        args.receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
