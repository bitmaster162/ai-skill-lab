"""Targeted U2 browser acceptance on intercepted, offline synthetic fixtures.
No production forms/events, real agency calls or Google requests are allowed.
"""
from __future__ import annotations
import json
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
from catalog import HEADERS, canonical, sha
from preview import ROOT, render, need
from test_catalog import AS_OF, rows_fixture, policy_fixture


def main() -> None:
    policy = policy_fixture()
    prepared = {kind: render(rows, policy, policy_sha=sha(canonical(policy)), as_of=AS_OF)[0]
                for kind, rows in [('synthetic', rows_fixture()), ('empty', [list(HEADERS)])]}
    records = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                                    headless=True, timeout=20000,
                                    args=['--disable-background-networking', '--no-first-run', '--disable-component-update'])
        try:
            for kind, files in prepared.items():
                config = json.loads(files['vercel.json'])
                csp = next(x['value'] for x in config['headers'][0]['headers'] if x['key'].lower() == 'content-security-policy')
                for locale in ('ru', 'en'):
                    route = '/phuket-universe' if locale == 'ru' else '/en/phuket-universe'
                    for enabled in (False, True):
                        for width in (390, 1440):
                            ctx = browser.new_context(java_script_enabled=enabled, viewport={'width': width, 'height': 844},
                                                      service_workers='block', offline=True)
                            page = ctx.new_page(); rejected = []; errors = []; requested = []
                            def fulfill(req):
                                url = urlsplit(req.request.url); requested.append(url.path)
                                if req.request.method != 'GET' or url.netloc != 'aiskillab.work':
                                    rejected.append(req.request.method + ' ' + req.request.url); req.abort(); return
                                if url.path == '/_vercel/insights/script.js':
                                    req.fulfill(status=200, body='', content_type='text/javascript'); return
                                key = url.path.lstrip('/')
                                if key not in files and key + '.html' in files: key += '.html'
                                if key not in files:
                                    rejected.append(key); req.abort(); return
                                mime = 'text/html; charset=utf-8' if key.endswith('.html') else 'text/css' if key.endswith('.css') else 'application/javascript' if key.endswith('.js') else 'font/woff2' if key.endswith('.woff2') else 'application/octet-stream'
                                req.fulfill(status=200, body=files[key], headers={'Content-Type': mime, 'Content-Security-Policy': csp})
                            ctx.route('**/*', fulfill)
                            page.on('pageerror', lambda error: errors.append(str(error)))
                            page.goto('https://aiskillab.work' + route, wait_until='load', timeout=18000)
                            page.evaluate('document.fonts.ready')
                            visible = lambda: page.locator('[data-u2-card]:visible').count()
                            need(page.locator('h1').count() == 1 and page.locator('form').count() == 0, 'semantics')
                            need(page.locator('#agency-pilot-terms').count() == 1, 'agency terms preserved')
                            need(page.locator('#homes [style]').count() == 0, 'inline style')
                            if not enabled:
                                need(visible() == (3 if kind == 'synthetic' else 0), 'all listings accessible without JS')
                                need(page.locator('#pu-type').is_disabled(), 'no-JS controls must not pretend to work')
                            else:
                                need(page.locator('#homes').get_attribute('data-u2-ready') == 'true', 'enhancement ready')
                                if kind == 'empty':
                                    need(visible() == 0 and 'Synthetic' not in page.locator('#homes').inner_text(), 'no invented listings')
                                else:
                                    need(visible() == 2, 'rent default')
                                    page.locator('[data-u2-deal="sale"]').click(); need(visible() == 1, 'sale switch')
                                    page.locator('[data-u2-deal="rent"]').click()
                                    page.locator('[data-u2-area="rawai"]').click(); need(visible() == 1, 'area')
                                    page.select_option('#pu-type', 'villa'); need(visible() == 0, 'combined no-match')
                                    page.locator('[data-u2-area=""]').click(); need(visible() == 1, 'type')
                                    page.select_option('#pu-beds', '4+'); need(visible() == 1, 'four-plus bedrooms')
                                    page.fill('#pu-price', '60000.49'); page.locator('[data-u2-apply]').click(); need(visible() == 0, 'exact price below')
                                    page.fill('#pu-price', '60000.50'); page.locator('[data-u2-apply]').click(); need(visible() == 1, 'exact price equal')
                                    page.fill('#pu-price', ''); page.select_option('#pu-type', ''); page.select_option('#pu-beds', '0')
                                    need(visible() == 1, 'studio filter')
                                    page.fill('#pu-price', '-1'); page.locator('[data-u2-apply]').click()
                                    need(page.locator('#pu-price').get_attribute('aria-invalid') == 'true' and visible() == 0, 'invalid price')
                                    page.fill('#pu-price', ''); page.select_option('#pu-beds', ''); page.locator('[data-u2-apply]').click()
                                    need(visible() == 2, 'filter reset')
                                    before = page.url
                                    page.evaluate("document.querySelector('#pu-price').focus()")
                                    page.keyboard.press('Enter'); need(page.url == before, 'Enter must not submit or leak price into URL')
                            dims = page.evaluate('({width:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight})')
                            need(dims['width'] <= width, 'horizontal overflow')
                            need(not rejected and not errors, 'unexpected network or JS error: ' + repr((rejected, errors)))
                            need(not any('google' in item for item in requested), 'browser Google fetch')
                            if kind == 'synthetic' and enabled and width == 390:
                                images = ROOT / 'review/u2_housing'; images.mkdir(parents=True, exist_ok=True)
                                page.locator('#homes').screenshot(path=str(images / (locale + '-synthetic-housing.png')))
                            records.append({'kind': kind, 'locale': locale, 'js': enabled, 'viewport': width,
                                            'visible': visible(), **dims, 'real_api_requests': 0, 'status': 'PASS'})
                            print('U2_BROWSER_PASS', json.dumps(records[-1]), flush=True)
                            ctx.close()
        finally:
            browser.close()
    print('U2_BROWSER_CASES', len(records), 'network_transmissions=0', flush=True)


if __name__ == '__main__': main()
