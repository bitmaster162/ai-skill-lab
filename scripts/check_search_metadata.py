#!/usr/bin/env python3
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import re
import sys
import xml.etree.ElementTree as ET
from datetime import date

from public_origin import PUBLIC_ORIGIN

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy" / "live"
ORIGIN = PUBLIC_ORIGIN
OG_IMAGE = f"{ORIGIN}/og.png"
RU_TITLE_CONTRACT = {
    "/faq": 'Вопросы и ответы — AI Skill Lab',
    "/privacy": 'Политика приватности — AI Skill Lab',
    "/safety": 'Безопасность детей и подростков — AI Skill Lab',
    "/terms": 'Условия обучения — AI Skill Lab',
}
RU_TITLE_SOURCE = {route: "app" + route + "/page.tsx" for route in RU_TITLE_CONTRACT}
TITLE_CONTRACT = {
    "/en/faq": "FAQ — sessions, projects and payment | AI Skill Lab",
    "/en/about": "About the practice and the method | AI Skill Lab",
    "/en/start": "Start — pick a track and a first task | AI Skill Lab",
    "/en/terms": "Terms of service | AI Skill Lab",
    "/en/privacy": "Privacy policy and data handling | AI Skill Lab",
    "/about": "О проекте: как устроены занятия | AI Skill Lab",
    "/parents": "Родителям: как проходят занятия и где участие взрослого.",
}


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


def source_page_for(route: str) -> Path:
    if route == "/":
        return ROOT / "app" / "page.tsx"
    return ROOT / "app" / route.lstrip("/") / "page.tsx"


def source_description(route: str) -> str | None:
    raw = source_page_for(route).read_text(encoding="utf-8")
    block = re.search(r"export const metadata[\s\S]*?=\s*\{([\s\S]*?)\};", raw)
    if not block:
        return None
    match = re.search(r"\bdescription\s*:\s*([\"'])(.*?)\1", block.group(0))
    return match.group(2).strip() if match else None


def source_title(route: str) -> str | None:
    raw = source_page_for(route).read_text(encoding="utf-8")
    block = re.search(r"export const metadata[\s\S]*?=\s*\{([\s\S]*?)\};", raw)
    if not block:
        return None
    text = block.group(0)
    absolute = re.search(r"\btitle\s*:\s*\{\s*absolute\s*:\s*([\"'])(.*?)\1\s*\}", text)
    if absolute:
        return absolute.group(2).strip()
    simple = re.search(r"\btitle\s*:\s*([\"'])(.*?)\1", text)
    if not simple:
        return None
    value = simple.group(2).strip()
    return value if route == "/" else f"{value} | AI Skill Lab"


def source_alternates(route: str) -> tuple[str | None, dict[str, str]]:
    raw = source_page_for(route).read_text(encoding="utf-8")
    block = re.search(r"export const metadata[\s\S]*?=\s*\{([\s\S]*?)\};", raw)
    if not block:
        return None, {}
    text = block.group(0)
    canonical_match = re.search(r"\bcanonical\s*:\s*([\"'])(.*?)\1", text)
    canonical = canonical_match.group(2).strip() if canonical_match else None
    languages_match = re.search(r"\blanguages\s*:\s*\{([\s\S]*?)\}", text)
    languages: dict[str, str] = {}
    if languages_match:
        lang_text = languages_match.group(1)
        for lang in ("ru", "en"):
            match = re.search(rf"\b{lang}\s*:\s*([\"'])(.*?)\1", lang_text)
            if match:
                languages[lang] = match.group(2).strip()
    return canonical, languages


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
        source_title_value = source_title(route)
        if source_title_value != title:
            fail(errors, route, f"source title {source_title_value!r} != static {title!r}")
        source_desc = source_description(route)
        if source_desc != desc:
            fail(errors, route, f"source description {source_desc!r} != static {desc!r}")
        source_canonical, source_languages = source_alternates(route)
        expected_source_canonical = "/" if route == "/" else route
        if source_canonical != expected_source_canonical:
            fail(errors, route, f"source canonical {source_canonical!r} != {expected_source_canonical!r}")
        source_ru, source_en, _ = paired_routes(route)
        expected_source_languages = {
            "ru": "/" if source_ru == "/" else source_ru,
            "en": source_en,
        }
        if source_languages != expected_source_languages:
            fail(errors, route, f"source languages {source_languages!r} != {expected_source_languages!r}")
        contracted_title = TITLE_CONTRACT.get(route)
        if contracted_title is not None and title != contracted_title:
            fail(errors, route, f"title {title!r} != contracted {contracted_title!r}")
        expected_title = RU_TITLE_CONTRACT.get(route)
        if expected_title is not None:
            if title != expected_title:
                fail(errors, route, f"title {title!r} != {expected_title!r}")
            source = read_source = (ROOT / RU_TITLE_SOURCE[route]).read_text(encoding="utf-8")
            marker = f'title: {{ absolute: "{expected_title}" }}'
            if marker not in source:
                fail(errors, route, "source absolute title contract missing")
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

    source_sitemap = (ROOT / "app/sitemap.ts").read_text(encoding="utf-8")
    source_lastmod = re.search(r'const lastModified = "(\d{4}-\d{2}-\d{2})";', source_sitemap)
    if not source_lastmod or source_sitemap.count("lastModified,") != 1:
        errors.append("source sitemap must expose one stable lastModified value")
    expected_lastmod = source_lastmod.group(1) if source_lastmod else None
    lastmod_urls = set()
    for entry in root.findall("sm:url", ns):
        loc = entry.find("sm:loc", ns)
        lastmod = entry.find("sm:lastmod", ns)
        if loc is None or not loc.text or lastmod is None or not lastmod.text:
            errors.append("every sitemap url must include loc and lastmod")
            continue
        loc_text = loc.text.strip()
        value = lastmod.text.strip()
        try:
            date.fromisoformat(value)
        except ValueError:
            errors.append(f"invalid sitemap lastmod {loc_text}: {value}")
        if expected_lastmod and value != expected_lastmod:
            errors.append(f"sitemap lastmod/source mismatch {loc_text}: {value} != {expected_lastmod}")
        lastmod_urls.add(loc_text)
    if lastmod_urls != expected_urls:
        errors.append("sitemap lastmod coverage must equal public route coverage")

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
