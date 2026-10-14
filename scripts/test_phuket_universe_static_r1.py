#!/usr/bin/env python3
"""Targeted acceptance for a local U1 static candidate, not a release waiver."""
from __future__ import annotations

import argparse
import json
import mimetypes
from pathlib import Path
import sys
import time
import unittest
from urllib.parse import unquote, urlsplit

import prepare_phuket_universe_static_r1 as candidate


class StaticU1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files, cls.stats = candidate.render()
        cls.parent = candidate.parent_payload()

    def test_deterministic_render_and_manifest(self):
        again, stats = candidate.render()
        self.assertEqual(again, self.files)
        self.assertEqual(stats, self.stats)
        payload = {n: b for n, b in self.files.items() if n != "_release.json"}
        candidate.verify_manifest(payload, self.files["_release.json"])

    def test_exact_delta_and_unchanged_parent(self):
        self.assertEqual(len(self.files), 105)
        self.assertEqual(set(self.files) - set(self.parent), candidate.NEW_FILES | {"_release.json"})
        self.assertEqual({n for n in self.parent if self.files[n] != self.parent[n]}, candidate.EDITED_PARENT_FILES)
        self.assertEqual(candidate.sha((candidate.ROOT / "deploy/live/_release.json").read_bytes()), candidate.BASE_MANIFEST)
        self.assertEqual(self.files["lab-command.js"], self.parent["lab-command.js"])
        self.assertEqual(self.files["vercel.json"], self.parent["vercel.json"])

    def test_svg_geometry_and_section_order(self):
        original = candidate.Page((candidate.ROOT / "design/PHUKET-UNIVERSE-MAKET-v2.html").read_text(encoding="utf-8"))
        geometry_tags = {"svg", "path", "circle", "ellipse", "filter", "fegaussianblur", "radialgradient", "stop"}
        def geometry(page):
            return [(tag, {k: v for k, v in attrs.items() if k not in {"style", "class", "aria-label"}})
                    for tag, attrs in page.tags if tag in geometry_tags]
        for route in candidate.ROUTES.values():
            page = candidate.Page(self.files[route.lstrip("/") + ".html"].decode("utf-8"))
            self.assertEqual(geometry(page), geometry(original))
            self.assertEqual([a.get("id") for tag, a in page.tags if tag == "section"], ["top", "orbit", "homes", "agencies"])

    def test_negative_payload_mutation_rejected(self):
        files = {n: b for n, b in self.files.items() if n != "_release.json"}
        files["phuket-universe.html"] += b"unexpected"
        with self.assertRaisesRegex(RuntimeError, "Payload bytes"):
            candidate.verify_manifest(files, self.files["_release.json"])

    def test_negative_duplicate_manifest_and_unsafe_paths(self):
        manifest = json.loads(self.files["_release.json"])
        manifest["files"].append(manifest["files"][0])
        with self.assertRaisesRegex(RuntimeError, "Duplicate"):
            candidate.verify_manifest({}, json.dumps(manifest).encode("utf-8"))
        for path in ("../outside", "/root", "C:/secret", "dir\\file"):
            with self.subTest(path=path):
                self.assertFalse(candidate.safe_path(path))

    def test_negative_csp_change_rejected(self):
        files = self.files.copy()
        files["vercel.json"] = b"{}"
        with self.assertRaisesRegex(RuntimeError, "byte-identical"):
            candidate.validate_pages(files, {})

    def test_authority_remains_off_and_copy_not_invented(self):
        for flag in ("release_authorized", "deploy_authorized", "production_ready"):
            self.assertIs(self.stats[flag], False)
        self.assertIn("SOURCE_AGENCY_TERMS_PLACEHOLDER_UNRESOLVED", self.stats["publication_holds"])
        ru = self.files["phuket-universe.html"].decode("utf-8")
        en = self.files["en/phuket-universe.html"].decode("utf-8")
        self.assertIn("[УСЛОВИЯ ДЛЯ АГЕНТСТВ]", ru)
        self.assertIn("[TERMS FOR AGENCIES]", en)
        self.assertEqual(self.stats["font_count"], 4)
        self.assertGreater(self.stats["font_bytes"], self.stats["parent_font_limit_bytes"])
        self.assertGreater(self.stats["non_font_bytes"], self.stats["parent_non_font_limit_bytes"])


def browser_acceptance(screenshots: bool = False) -> list[dict]:
    import psutil
    from playwright.sync_api import sync_playwright
    candidate.need(psutil.virtual_memory().available >= 2 * 1024**3,
                   "HOST_MEMORY_HOLD: inherited local browser floor is 2 GiB")
    exe = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
    candidate.need(exe.is_file(), "Known isolated test browser unavailable")
    files, stats = candidate.render()
    config = json.loads(files["vercel.json"])
    headers = {h["key"]: h["value"] for rule in config["headers"] if rule["source"] == "/(.*)" for h in rule["headers"]}
    image_dir = candidate.ROOT / "review" / candidate.RELEASE
    if screenshots:
        image_dir.mkdir(parents=True, exist_ok=False)
    results = []
    start = time.monotonic()
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(exe), headless=True, timeout=20000,
            args=["--disable-background-networking", "--disable-component-update", "--no-first-run"])
        try:
            for locale, route_path in candidate.ROUTES.items():
                for enabled in (False, True):
                    for width in (390, 1440):
                        candidate.need(time.monotonic() - start < 110, "Browser acceptance wall budget exceeded")
                        ctx = browser.new_context(java_script_enabled=enabled, offline=True,
                            service_workers="block", viewport={"width": width, "height": 844 if width == 390 else 900})
                        ctx.set_default_timeout(6000)
                        page = ctx.new_page()
                        blocked, events, errors, fonts = [], [], [], []
                        page.on("pageerror", lambda e: errors.append(str(e)))
                        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
                        def fulfill(rt):
                            req = rt.request
                            u = urlsplit(req.url)
                            if u.scheme != "https" or u.netloc != "aiskillab.work":
                                blocked.append(req.url); rt.abort(); return
                            if u.path == "/api/event" and req.method == "POST":
                                body = json.loads(req.post_data or "{}")
                                events.append({"body": body, "url": req.url})
                                rt.fulfill(status=200, body='{"ok":true}', headers={"Content-Type": "application/json"}); return
                            if req.method != "GET" or u.query:
                                blocked.append(req.url); rt.abort(); return
                            if u.path == "/_vercel/insights/script.js":
                                rt.fulfill(status=200, body="/* isolated analytics stub: no transmission */", headers={"Content-Type": "application/javascript"}); return
                            path = unquote(u.path).lstrip("/")
                            name = path if path in files else path + ".html"
                            if not candidate.safe_path(name) or name not in files:
                                blocked.append(req.url); rt.abort(); return
                            if name.endswith(".woff2"):
                                fonts.append(name)
                            kind = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
                                    ".js": "application/javascript", ".woff2": "font/woff2"}.get(Path(name).suffix)
                            kind = kind or mimetypes.guess_type(name)[0] or "application/octet-stream"
                            rt.fulfill(status=200, body=files[name], headers={**headers, "Content-Type": kind})
                        ctx.route("**/*", fulfill)
                        response = page.goto(candidate.ORIGIN + route_path, wait_until="load", timeout=15000)
                        page.evaluate("document.fonts.ready")
                        layout = page.evaluate("""() => ({
                            width: document.documentElement.scrollWidth,
                            viewport: innerWidth,
                            height: document.documentElement.scrollHeight,
                            svg: document.querySelectorAll('.pu-page svg').length,
                            h1: document.querySelectorAll('h1').length,
                            bg: getComputedStyle(document.querySelector('.pu-page')).backgroundColor,
                            font: getComputedStyle(document.querySelector('.pu-page>div')).fontFamily,
                            headingsFont: getComputedStyle(document.querySelector('h1')).fontFamily,
                            inlineStyles: document.querySelectorAll('[style],style').length,
                            forms: document.forms.length,
                            allDisabled: [...document.querySelectorAll('.pu-page button,.pu-page input,.pu-page select')].every(e=>e.disabled)
                        })""")
                        candidate.need(response is not None and response.status == 200, "Fixture HTTP response")
                        candidate.need(layout["width"] <= width + 1 and layout["svg"] == 8 and layout["h1"] == 1, "Layout/geometry failed")
                        candidate.need(layout["bg"] == "rgb(7, 10, 18)" and "Manrope" in layout["font"] and "Unbounded" in layout["headingsFont"], "Design tokens failed")
                        candidate.need(layout["inlineStyles"] == 0 and layout["forms"] == 0 and layout["allDisabled"], "CSP/form readiness failed")
                        candidate.need("fonts/Unbounded-ru-en.woff2" in fonts and any("Manrope" in f for f in fonts), "Self-hosted fonts not loaded")
                        if enabled:
                            page.evaluate("""() => {
                                for (const href of ['https://cal.com/fixture','https://t.me/fixture','https://wa.me/1000','https://line.me/fixture','mailto:test@example.invalid']) {
                                    const a=document.createElement('a');a.href=href;
                                    a.addEventListener('click',e=>e.preventDefault());document.body.appendChild(a);
                                    a.click();a.remove();
                                }
                                for (const event of ['lead_submit_ok','lead_submit_error']) dispatchEvent(new CustomEvent('asl:lead-event',{detail:{event}}));
                            }""")
                            page.wait_for_timeout(100)
                            expected = ["cal_click", "telegram_click", "whatsapp_click", "line_click", "email_click", "lead_submit_ok", "lead_submit_error"]
                            candidate.need(len(events) == 7, "Expected seven mocked E3.8 events")
                            for i, event in enumerate(events):
                                candidate.need(event["body"] == {"event": expected[i], "page": route_path, "locale": locale}, "Unexpected event payload or PII")
                        else:
                            candidate.need(not events, "No-JS event request")
                        candidate.need(not blocked and not errors, "Browser failures " + repr((blocked, errors)))
                        if screenshots and locale == "ru" and not enabled:
                            page.screenshot(path=str(image_dir / f"ru-{width}.png"), full_page=False)
                        item = {"locale": locale, "js": enabled, **layout, "events_mocked": len(events),
                                "font_files_loaded": fonts, "external_requests_continued": 0, "status": "PASS"}
                        results.append(item)
                        print("BROWSER_ACCEPTANCE", json.dumps(item, ensure_ascii=True), flush=True)
                        ctx.close()
        finally:
            browser.close()
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", action="store_true")
    parser.add_argument("--screenshots", action="store_true")
    args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(StaticU1Tests))
    if not result.wasSuccessful():
        raise SystemExit(1)
    if args.browser:
        cases = browser_acceptance(args.screenshots)
        print("STATIC_U1_BROWSER_PASS", len(cases), "real_api_requests=0", flush=True)
    print("STATIC_U1_PREPARATION_ACCEPTED_PUBLICATION_HOLD", flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
