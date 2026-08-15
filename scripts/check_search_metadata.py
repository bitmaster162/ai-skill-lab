#!/usr/bin/env python3
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy" / "live"
ORIGIN = "https://ai-skill-lab.vercel.app"
OG_IMAGE = f"{ORIGIN}/og.png"


def route_for(path: Path) -> str:
    rel = path.relative_to(LIVE).as_posix()
    if rel == "index.html":
        return "/"
    if rel == "en.html":
        return "/en"
    return "/" + rel.removesuffix(".html")


def paired_routes(route: str) -> tuple[str, str, str]:
    if route == "/en":
        return "/", "/en", "/"
    if route.startswith("/en/"):
        ru = route[3:] or "/"
        return ru, route, ru
    en = "/en" if route == "/" else "/en" + route
    return route, en, route


class HeadParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_head = False
        self.in_title = False
        self.title = ""
        self.html_lang = ""
        self.meta_name: dict[str, str] = {}
        self.meta_property: dict[str, str] = {}
        self.links: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "html":
            self.html_lang = a.get("lang", "")
        elif tag == "head":
            self.in_head = True
        elif self.in_head and tag == "title":
            self.in_title = True
        elif self.in_head and tag == "meta":
            content = a.get("content", "").strip()
            if a.get("name"):
                self.meta_name[a["name"].lower()] = content
            if a.get("property"):
                self.meta_property[a["property"].lower()] = content
        elif self.in_head and tag == "link":
            self.links.append(a)

    def handle_endtag(self, tag: str) -> None:
        if tag == "head":
            self.in_head = False
        elif tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title += data


def one_link(p: HeadParser, rel: str, hreflang: str | None = None) -> str | None:
    found = []
    for link in p.links:
        rels = set(link.get("rel", "").lower().split())
        if rel not in rels:
            continue
        if hreflang is not None and link.get("hreflang", "").lower() != hreflang:
            continue
        found.append(link.get("href", ""))
    return found[0] if len(found) == 1 else None


def fail(errors: list[str], route: str, msg: str) -> None:
    errors.append(f"{route}: {msg}")


def main() -> int:
    errors: list[str] = []
    public_routes: set[str] = set()
    checked = 0

    pages = sorted(LIVE.rglob("*.html"))
    for path in pages:
        route = route_for(path)
        parser = HeadParser()
        parser.feed(path.read_text(encoding="utf-8"))
        checked += 1

        if route == "/404":
            robots = parser.meta_name.get("robots", "").lower()
            if "noindex" not in robots:
                fail(errors, route, "404 must be noindex")
            continue

        public_routes.add(route)
        expected_lang = "en" if route == "/en" or route.startswith("/en/") else "ru"
        if parser.html_lang != expected_lang:
            fail(errors, route, f"html lang={parser.html_lang!r}, expected {expected_lang!r}")

        title = re.sub(r"\s+", " ", parser.title).strip()
        desc = parser.meta_name.get("description", "").strip()
        if not (15 <= len(title) <= 65):
            fail(errors, route, f"title length {len(title)} outside 15..65")
        if not (50 <= len(desc) <= 160):
            fail(errors, route, f"description length {len(desc)} outside 50..160")

        expected_url = ORIGIN + ("/" if route == "/" else route)
        canonical = one_link(parser, "canonical")
        if canonical != expected_url:
            fail(errors, route, f"canonical {canonical!r} != {expected_url!r}")

        ru, en, xdefault = paired_routes(route)
        expected_alt = {
            "ru": ORIGIN + ("/" if ru == "/" else ru),
            "en": ORIGIN + en,
            "x-default": ORIGIN + ("/" if xdefault == "/" else xdefault),
        }
        for lang, expected in expected_alt.items():
            actual = one_link(parser, "alternate", lang)
            if actual != expected:
                fail(errors, route, f"hreflang {lang} {actual!r} != {expected!r}")

        og = parser.meta_property
        if og.get("og:type") != "website":
            fail(errors, route, "og:type must be website")
        if og.get("og:site_name") != "AI Skill Lab":
            fail(errors, route, "og:site_name must be AI Skill Lab")
        if og.get("og:title") != title:
            fail(errors, route, "og:title must equal document title")
        if og.get("og:description") != desc:
            fail(errors, route, "og:description must equal meta description")
        if og.get("og:url") != expected_url:
            fail(errors, route, "og:url must equal canonical")
        if og.get("og:image") != OG_IMAGE:
            fail(errors, route, "og:image must use canonical site OG image")

        twitter = parser.meta_name
        if twitter.get("twitter:card") != "summary_large_image":
            fail(errors, route, "twitter:card must be summary_large_image")
        # Some older static pages inherited only the card. Require full deterministic sharing metadata now.
        if twitter.get("twitter:title") != title:
            fail(errors, route, "twitter:title must equal document title")
        if twitter.get("twitter:description") != desc:
            fail(errors, route, "twitter:description must equal meta description")
        if twitter.get("twitter:image") != OG_IMAGE:
            fail(errors, route, "twitter:image must use canonical site OG image")

    sitemap = LIVE / "sitemap.xml"
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    root = ET.parse(sitemap).getroot()
    sitemap_urls = {node.text.strip() for node in root.findall("sm:url/sm:loc", ns) if node.text}
    expected_urls = {ORIGIN + ("/" if r == "/" else r) for r in public_routes}
    if sitemap_urls != expected_urls:
        missing = sorted(expected_urls - sitemap_urls)
        extra = sorted(sitemap_urls - expected_urls)
        errors.append(f"sitemap mismatch missing={missing} extra={extra}")

    robots = (LIVE / "robots.txt").read_text(encoding="utf-8")
    if "User-agent: *" not in robots or "Allow: /" not in robots:
        errors.append("robots.txt must allow public crawling")
    if f"Sitemap: {ORIGIN}/sitemap.xml" not in robots:
        errors.append("robots.txt sitemap origin mismatch")

    if errors:
        print("SEARCH_METADATA_FAIL")
        for e in errors:
            print("-", e)
        return 1

    print(f"SEARCH_METADATA_PASS pages={checked} public_routes={len(public_routes)} sitemap={len(sitemap_urls)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
