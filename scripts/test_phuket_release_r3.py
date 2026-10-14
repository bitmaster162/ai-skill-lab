#!/usr/bin/env python3
"""Local U1 R3 acceptance: exact lineage, negative cases and offline browser.

No live HTTP requests, no writes to payloads, and no release authority.
Browser requests are fulfilled from the checked-in static files in memory.
"""
from __future__ import annotations
import argparse
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import build_phuket_release_r3 as builder
import phuket_release_profile as profile


class R3Acceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = {p.relative_to(profile.LIVE).as_posix(): p.read_bytes()
                     for p in profile.LIVE.rglob("*") if p.is_file()}
        cls.parent = builder.parent_payload()

    def test_exact_identity_and_inherited_payload(self):
        result = profile.verify_integrity()
        self.assertEqual((result["files"], result["routes"], result["workshop_routes"]), (104, 56, 54))
        self.assertEqual(sum(self.files[n] == data for n, data in self.parent.items()), 96)
        self.assertEqual(self.files["vercel.json"], self.parent["vercel.json"])
        self.assertEqual(self.files["lab-command.js"], self.parent["lab-command.js"])

    def test_regeneration_is_byte_identical(self):
        self.assertEqual(builder.render(), self.files)

    def test_svg_geometry_and_contact_contract(self):
        original = profile.Tags((profile.ROOT / "design/PHUKET-UNIVERSE-MAKET-v2.html").read_text(encoding="utf-8"))
        geometry_tags = {"svg", "path", "circle", "ellipse", "filter", "fegaussianblur", "radialgradient", "stop"}
        def geometry(page):
            return [(t, {k: v for k, v in a.items() if k not in {"style", "class", "aria-label"}})
                    for t, a in page.tags if t in geometry_tags]
        hosts = {"phuketravel.vercel.app", "stasph.vercel.app", "muaithaiph.vercel.app", "haven-ruddy.vercel.app", "rostikson-portfolio.vercel.app"}
        from urllib.parse import urlsplit
        for name in sorted(profile.UNIVERSE_FILES):
            text = self.files[name].decode("utf-8")
            doc = profile.Tags(text)
            self.assertEqual(geometry(doc), geometry(original))
            links = [a for t, a in doc.tags if t == "a" and a.get("href", "").startswith("https://")]
            self.assertEqual(sum(urlsplit(a["href"]).hostname in hosts for a in links), 10)
            self.assertTrue(all("noopener" in a.get("rel", "").split() for a in links))
            self.assertEqual(sum(a.get("href", "").startswith("mailto:robert@aiskillab.work") for t, a in doc.tags if t == "a"), 2)
            self.assertNotIn("[TERMS FOR AGENCIES]", text)
            self.assertNotIn("[УСЛОВИЯ ДЛЯ АГЕНТСТВ]", text)
            self.assertTrue(profile.universe_page(profile.LIVE / name))

    def test_one_byte_payload_change_denied(self):
        target = profile.LIVE / "phuket-universe.html"
        old_read = Path.read_bytes
        def changed(path):
            raw = old_read(path)
            return raw + b"altered" if path == target else raw
        with patch.object(Path, "read_bytes", changed):
            with self.assertRaisesRegex(ValueError, "payload differs"):
                profile.verify_integrity()

    def test_duplicate_manifest_denied(self):
        target = profile.LIVE / "_release.json"
        manifest = json.loads(self.files["_release.json"])
        manifest["files"][1] = manifest["files"][0]
        old_read = Path.read_text
        def changed(path, *args, **kwargs):
            return json.dumps(manifest) if path == target else old_read(path, *args, **kwargs)
        with patch.object(Path, "read_text", changed):
            with self.assertRaisesRegex(ValueError, "duplicate/missing"):
                profile.verify_integrity()

    def test_authority_budget_and_parent_pin_mutations_denied(self):
        target = profile.ROOT / "data/phuket_universe_u1_static_r3_profile.json"
        good = profile.profile()
        variants = []
        changed = copy.deepcopy(good); changed["authority"]["deploy"] = True; variants.append(changed)
        changed = copy.deepcopy(good); changed["budgets"]["payload_max_bytes"] += 1; variants.append(changed)
        changed = copy.deepcopy(good); changed["parent_file_pins"]["index.html"]["sha256"] = "0" * 64; variants.append(changed)
        changed = copy.deepcopy(good); changed["universe_routes"].append("/not-approved"); variants.append(changed)
        old_read = Path.read_text
        for value in variants:
            def patched_read(path, *args, **kwargs):
                return json.dumps(value) if path == target else old_read(path, *args, **kwargs)
            with self.subTest(mutation=variants.index(value)), patch.object(Path, "read_text", patched_read):
                with self.assertRaises(ValueError):
                    profile.verify_integrity()

    def test_old_and_new_route_admission_fail_closed(self):
        import guide_route_admission as routes
        self.assertEqual(routes.admitted_route_count(), 56)
        self.assertEqual(routes.require_route_set(routes.admitted_routes()), 56)
        for bad in (routes.admitted_routes() - {"/phuket-universe"}, routes.admitted_routes() | {"/unapproved"}):
            with self.assertRaises(routes.RouteAdmissionError):
                routes.require_route_set(bad)
        self.assertEqual(routes.require_route_set(routes.BASELINE_ROUTES, approved_slugs=[]), 52)
        with self.assertRaises(routes.RouteAdmissionError):
            routes.require_route_set(routes.BASELINE_ROUTES | profile.UNIVERSE_ROUTES, approved_slugs=[])


def run_units() -> None:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(R3Acceptance)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


def browser_acceptance() -> list[dict]:
    from urllib.parse import urlsplit, unquote
    import time
    import psutil
    from playwright.sync_api import sync_playwright
    if psutil.virtual_memory().available < 2 * 1024**3:
        raise RuntimeError("HOST_RESOURCE_HOLD")
    files = {p.relative_to(profile.LIVE).as_posix(): p.read_bytes() for p in profile.LIVE.rglob("*") if p.is_file()}
    profile.verify_integrity()
    config = json.loads(files["vercel.json"])
    headers = {h["key"]: h["value"] for row in config["headers"] if row["source"] == "/(.*)" for h in row["headers"]}
    exe = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
    if not exe.is_file():
        raise RuntimeError("KNOWN_BROWSER_UNAVAILABLE")
    cases = []
    started = time.monotonic()
    with sync_playwright() as engine:
        browser = engine.chromium.launch(executable_path=str(exe), headless=True, timeout=20000,
            args=["--disable-background-networking", "--disable-component-update", "--no-first-run"])
        try:
            for locale in ("ru", "en"):
                route = "/phuket-universe" if locale == "ru" else "/en/phuket-universe"
                for enabled in (False, True):
                    for width in (390, 1440):
                        if time.monotonic() - started > 110:
                            raise RuntimeError("BROWSER_ACCEPTANCE_TIME_HOLD")
                        ctx = browser.new_context(java_script_enabled=enabled, offline=True, service_workers="block",
                            viewport={"width": width, "height": 844 if width == 390 else 900})
                        ctx.set_default_timeout(6000)
                        page = ctx.new_page()
                        rejected, events, errors, fonts = [], [], [], set()
                        page.on("pageerror", lambda e: errors.append(str(e)))
                        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
                        def fulfill(request):
                            req = request.request
                            url = urlsplit(req.url)
                            if url.scheme != "https" or url.netloc != "aiskillab.work":
                                rejected.append(req.url); request.abort(); return
                            if url.path == "/api/event" and req.method == "POST":
                                events.append(json.loads(req.post_data or "{}"))
                                request.fulfill(status=200, body='{"ok":true}', headers={"Content-Type": "application/json"}); return
                            if req.method != "GET" or url.query:
                                rejected.append(req.url); request.abort(); return
                            if url.path == "/_vercel/insights/script.js":
                                request.fulfill(status=200, body="/* offline analytics stub */", headers={"Content-Type": "application/javascript"}); return
                            name = unquote(url.path).lstrip("/")
                            if name not in files: name += ".html"
                            if name not in files or ".." in Path(name).parts:
                                rejected.append(req.url); request.abort(); return
                            if name.endswith(".woff2"): fonts.add(name)
                            kind = {".html": "text/html; charset=utf-8", ".js": "application/javascript", ".css": "text/css; charset=utf-8", ".woff2": "font/woff2"}.get(Path(name).suffix, "application/octet-stream")
                            request.fulfill(status=200, body=files[name], headers={**headers, "Content-Type": kind})
                        ctx.route("**/*", fulfill)
                        response = page.goto("https://aiskillab.work" + route, wait_until="load", timeout=15000)
                        page.evaluate("document.fonts.ready")
                        view = page.evaluate("""() => ({width: document.documentElement.scrollWidth, height: document.documentElement.scrollHeight,
                            h1: document.querySelectorAll('h1').length, svg: document.querySelectorAll('.pu-page svg').length,
                            inlineStyles: document.querySelectorAll('[style],style').length, forms: document.forms.length,
                            disabled: [...document.querySelectorAll('.pu-page button,.pu-page select,.pu-page input')].every(e=>e.disabled),
                            font: getComputedStyle(document.querySelector('.pu-page>div')).fontFamily,
                            titleFont: getComputedStyle(document.querySelector('h1')).fontFamily,
                            skip: document.querySelector('a.pu-skip-link')?.getAttribute('href')})""")
                        if response is None or response.status != 200 or view["width"] > width + 1 or view["h1"] != 1 or view["svg"] != 8:
                            raise ValueError("U1 viewport/semantics failed")
                        if view["inlineStyles"] or view["forms"] or not view["disabled"] or view["skip"] != "#main":
                            raise ValueError("U1 security/accessibility failed")
                        if "Manrope" not in view["font"] or "Unbounded" not in view["titleFont"] or "fonts/Unbounded-ru-en.woff2" not in fonts:
                            raise ValueError("U1 local fonts failed")
                        expected_fonts = {"fonts/Unbounded-ru-en.woff2", "fonts/Manrope-latin.woff2"}
                        if locale == "ru": expected_fonts.add("fonts/Manrope-cyrillic.woff2")
                        if fonts != expected_fonts:
                            raise ValueError("Unexpected loaded font set")
                        if enabled:
                            page.evaluate("""() => {
                                for (const href of ['https://cal.com/fixture','https://t.me/fixture','https://wa.me/1000','https://line.me/fixture','mailto:test@example.invalid']) {
                                    const a = document.createElement('a'); a.href=href; a.addEventListener('click',e=>e.preventDefault());
                                    document.body.appendChild(a); a.click(); a.remove();
                                }
                                for (const event of ['lead_submit_ok','lead_submit_error']) dispatchEvent(new CustomEvent('asl:lead-event',{detail:{event}}));
                            }""")
                            page.wait_for_timeout(100)
                            wanted = ["cal_click", "telegram_click", "whatsapp_click", "line_click", "email_click", "lead_submit_ok", "lead_submit_error"]
                            if events != [{"event": name, "page": route, "locale": locale} for name in wanted]:
                                raise ValueError("Existing E3.8 mock contract changed")
                        elif events:
                            raise ValueError("No-JS must not send events")
                        if rejected or errors:
                            raise ValueError("Browser request/CSP error: " + repr((rejected, errors)))
                        item = {"locale": locale, "js": enabled, "viewport": width, **view, "fonts_loaded": sorted(fonts), "events_mocked": len(events), "status": "PASS"}
                        print("R3_BROWSER_ACCEPTANCE " + json.dumps(item, ensure_ascii=True), flush=True)
                        cases.append(item)
                        ctx.close()
        finally:
            browser.close()
    return cases


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", action="store_true")
    args = parser.parse_args()
    run_units()
    if args.browser:
        cases = browser_acceptance()
        print("R3_BROWSER_PASS cases=" + str(len(cases)) + " real_api_requests=0")
    print("R3_TARGETED_ACCEPTANCE_PASS_LOCAL_ONLY")
