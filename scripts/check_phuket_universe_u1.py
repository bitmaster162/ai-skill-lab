#!/usr/bin/env python3
"""Targeted U1 acceptance only: source fidelity, CSP, no-JS browser, mobile."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
raw = (ROOT / "components/phuketUniverseMarkup.ts").read_text(encoding="utf-8")
markup = json.loads(raw.split("export const phuketUniverseMarkup = ", 1)[1].rsplit(" as const;", 1)[0])
source_bytes = (ROOT / "design/PHUKET-UNIVERSE-MAKET-v2.html").read_bytes()
assert hashlib.sha256(source_bytes).hexdigest() == "2d5112f138e7364a83b15471179b5767891e3448e188f0f566d139702dd97024", "U1 source pin changed"
original = source_bytes.decode("utf-8")
css = (ROOT / "app/phuket-universe.css").read_text(encoding="utf-8")
svg_paths = re.findall(r'<path\b[^>]*\bd="([^"]+)"', original)
svg_ellipses = re.findall(r'<ellipse\b[^>]*\brx="([^"]+)"[^>]*\bry="([^"]+)"', original)
svg_count = original.count("<svg ")
hosts = ("phuketravel.vercel.app", "stasph.vercel.app", "muaithaiph.vercel.app",
         "haven-ruddy.vercel.app", "rostikson-portfolio.vercel.app")
sections = ("top", "orbit", "homes", "agencies")
for locale in ("ru", "en"):
    doc = markup[locale]
    assert doc.count("<svg ") == svg_count
    assert re.findall(r'<path\b[^>]*\bd="([^"]+)"', doc) == svg_paths
    assert re.findall(r'<ellipse\b[^>]*\brx="([^"]+)"[^>]*\bry="([^"]+)"', doc) == svg_ellipses
    assert doc.count('rel="noopener"') == 11
    assert all(doc.count("https://" + host + '"') == 2 for host in hosts)
    assert "<form " not in doc and "disabled" in doc
    assert not re.search(r'<(?:script|style)\b|\sstyle=', doc, re.I)
    assert not re.search(r'fonts\.googleapis|fonts\.gstatic', doc, re.I)
    if locale == "en":
        assert not re.search(r'[\u0400-\u04ff]', doc)
    print("SOURCE_PASS", locale, "svg", svg_count, "friend_links", 10, flush=True)

for fname in ("Manrope-cyrillic.woff2", "Manrope-latin.woff2"):
    assert (ROOT / "public/fonts" / fname).read_bytes().startswith(b"wOF2")
assert "@font-face" in css and "fonts.gstatic" not in css
v = json.loads((ROOT / "deploy/live/vercel.json").read_text(encoding="utf-8"))
policy = next(h["value"] for h in v["headers"][0]["headers"] if h["key"] == "Content-Security-Policy")
assert "style-src 'self'" in policy and "font-src 'self'" in policy
static_css = ("globals.css", "r69.css", "r70.css", "commercial-mobile.css",
              "proof-contrast.css", "phuket-universe.css")
route_css = {"/" + f: ROOT / "app" / f for f in static_css}
assert all(p.is_file() for p in route_css.values()), "missing CSS"
base = "https://aiskillab.work"
chrome = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if sys.argv[1:] == ["--source-only"]:
    print("U1_SOURCE_CSP_PASS routes=2 svgs=8 partner_links=10 browser=NOT_RUN", flush=True)
    raise SystemExit(0)
if sys.argv[1:]:
    raise SystemExit("U1 unknown check argument")
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=chrome, headless=True, timeout=20000,
        args=["--disable-background-networking", "--no-first-run", "--disable-component-update"])
    try:
        for locale in ("ru", "en"):
            route_path = "/phuket-universe" if locale == "ru" else "/en/phuket-universe"
            body = '<div class="pu-page" lang="' + locale + '">' + markup[locale] + "</div>"
            head = "".join('<link rel="stylesheet" href="/' + item + '">' for item in static_css)
            page_html = ('<!doctype html><html lang="' + locale
                         + '"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
                         + head + "</head><body>" + body + "</body></html>")
            for width in (390, 1440):
                ctx = browser.new_context(viewport={"width": width, "height": 844 if width == 390 else 900},
                                          java_script_enabled=False, service_workers="block", offline=True)
                page = ctx.new_page()
                unexpected = []
                def fulfill(req):
                    target = urlsplit(req.request.url)
                    if target.scheme != "https" or target.netloc != "aiskillab.work":
                        unexpected.append(req.request.url)
                        req.abort()
                    elif target.path == route_path:
                        req.fulfill(status=200, body=page_html.encode("utf-8"),
                                    headers={"Content-Type": "text/html; charset=utf-8", "Content-Security-Policy": policy})
                    elif target.path in route_css:
                        req.fulfill(status=200, body=route_css[target.path].read_bytes(),
                                    headers={"Content-Type": "text/css; charset=utf-8", "Content-Security-Policy": policy})
                    elif target.path.startswith("/fonts/") and (ROOT / "public" / target.path.lstrip("/")).is_file():
                        req.fulfill(status=200, body=(ROOT / "public" / target.path.lstrip("/")).read_bytes(),
                                    headers={"Content-Type": "font/woff2", "Content-Security-Policy": policy})
                    else:
                        unexpected.append(req.request.url)
                        req.abort()
                ctx.route("**/*", fulfill)
                resp = page.goto(base + route_path, wait_until="load", timeout=15000)
                details = page.evaluate("""() => ({
                    h1: document.querySelectorAll('.pu-page h1').length,
                    sections: [...document.querySelectorAll('.pu-page section[id]')].map(x=>x.id),
                    svgs: document.querySelectorAll('.pu-page svg').length,
                    externalProjects: [...document.querySelectorAll('.pu-page a[href^="https://"]')].filter(
                        x=>x.hostname !== 'aiskillab.work').length,
                    disabledButtons: [...document.querySelectorAll('.pu-page button')].every(b=>b.disabled),
                    width: document.documentElement.scrollWidth,
                    viewport: window.innerWidth,
                    bg: getComputedStyle(document.querySelector('.pu-page')).backgroundColor,
                    font: getComputedStyle(document.querySelector('.pu-page > div')).fontFamily,
                    unsafeInline: document.querySelectorAll('.pu-page [style],.pu-page script,.pu-page style').length
                })""")
                assert resp is not None and resp.status == 200, "mock route status"
                assert details["h1"] == 1 and details["sections"] == list(sections), "semantics"
                assert details["svgs"] == svg_count and details["externalProjects"] == 10, "SVG/project links"
                assert details["disabledButtons"] and details["unsafeInline"] == 0, "no-JS safety"
                assert details["width"] <= details["viewport"] + 1, "horizontal overflow"
                assert details["bg"] == "rgb(7, 10, 18)", "palette mismatch"
                assert "Manrope" in details["font"], "local font not applied"
                assert not unexpected, "unexpected network request: " + repr(unexpected[:2])
                print("BROWSER_PASS", locale, width, "height", page.evaluate("document.documentElement.scrollHeight"), flush=True)
                ctx.close()
    finally:
        browser.close()
print("U1_ACCEPTANCE_PASS_LOCAL_ONLY", flush=True)
