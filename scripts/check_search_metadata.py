#!/usr/bin/env python3
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import date

from public_origin import PUBLIC_ORIGIN

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy" / "live"
ORIGIN = PUBLIC_ORIGIN
OG_IMAGE = f"{ORIGIN}/og.png"
DESCRIPTION_120_155 = {
    "/business",
    "/teens",
    "/faq",
    "/personal",
    "/en/teens",
    "/kids",
    "/en/business",
    "/en/kids",
    "/en/personal",
    "/en/faq",
    "/en/phuket",
    "/en/safety",
    "/method",
    "/privacy",
    "/en/method",
    "/en/privacy",
    "/en/curriculum",
    "/en/matcher",
    "/curriculum",
    "/phuket",
    "/terms",
    "/proof",
    "/safety",
    "/en/start",
}
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


def source_layout_contract() -> tuple[list[Path], bool]:
    app = ROOT / "app"
    single = app / "layout.tsx"
    ru = app / "(ru)" / "layout.tsx"
    en = app / "(en)" / "layout.tsx"
    if single.exists():
        return [single], False
    if ru.exists() and en.exists():
        return [ru, en], True
    return [], False


def source_page_for(route: str) -> Path:
    app = ROOT / "app"
    _, grouped = source_layout_contract()
    if grouped:
        if route == "/":
            return app / "(ru)" / "page.tsx"
        if route == "/en":
            return app / "(en)" / "en" / "page.tsx"
        if route.startswith("/en/"):
            return app / "(en)" / "en" / route.removeprefix("/en/") / "page.tsx"
        return app / "(ru)" / route.lstrip("/") / "page.tsx"
    if route == "/":
        return app / "page.tsx"
    return app / route.lstrip("/") / "page.tsx"


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


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def latest_public_html_commit_date(paths: list[Path], errors: list[str]) -> date | None:
    try:
        shallow = git("rev-parse", "--is-shallow-repository").lower() == "true"
    except (OSError, subprocess.CalledProcessError) as exc:
        errors.append(f"cannot inspect git history for sitemap freshness: {exc}")
        return None
    if shallow:
        if os.environ.get("CI", "").lower() == "true":
            errors.append("CI checkout must provide full git history for sitemap freshness")
        return None

    dates: list[date] = []
    for path in paths:
        rel = path.relative_to(ROOT).as_posix()
        try:
            raw = git("log", "-1", "--format=%cs", "--", rel)
        except subprocess.CalledProcessError as exc:
            errors.append(f"cannot read git history for {rel}: {exc}")
            continue
        if not raw:
            errors.append(f"missing git commit history for {rel}")
            continue
        try:
            dates.append(date.fromisoformat(raw))
        except ValueError:
            errors.append(f"invalid git commit date for {rel}: {raw}")
    return max(dates) if dates else None


def fail(errors: list[str], route: str, msg: str) -> None:
    errors.append(f"{route}: {msg}")


def main() -> int:
    errors: list[str] = []
    public_routes: set[str] = set()
    checked = 0

    source_layout_paths, grouped_layouts = source_layout_contract()
    if not source_layout_paths:
        errors.append("source root layout contract missing")
        source_layouts: list[tuple[Path, str]] = []
    else:
        source_layouts = [(path, path.read_text(encoding="utf-8")) for path in source_layout_paths]

    for source_layout_path, source_layout in source_layouts:
        rel_layout = source_layout_path.relative_to(ROOT)
        if source_layout.count('"/og.png"') != 2:
            errors.append(f"{rel_layout} must use /og.png for both OpenGraph and Twitter images")
        if '"/opengraph-image"' in source_layout:
            errors.append(f"{rel_layout} must not use dynamic /opengraph-image as social image authority")
        if 'manifest: "/site.webmanifest"' not in source_layout:
            errors.append(f"{rel_layout} must declare /site.webmanifest")
        if 'url: "/favicon.svg"' not in source_layout:
            errors.append(f"{rel_layout} must declare /favicon.svg as icon authority")
        if 'url: "/favicon.ico"' not in source_layout:
            errors.append(f"{rel_layout} must declare /favicon.ico fallback")
        if 'url: "/apple-touch-icon.png"' not in source_layout:
            errors.append(f"{rel_layout} must declare /apple-touch-icon.png")
        if 'themeColor: "#0b0d10"' not in source_layout:
            errors.append(f"{rel_layout} must declare production theme color #0b0d10")

    if grouped_layouts:
        grouped = {path.parent.name: text for path, text in source_layouts}
        if '<html lang="ru">' not in grouped.get("(ru)", ""):
            errors.append("app/(ru)/layout.tsx must declare html lang=ru")
        if '<html lang="en">' not in grouped.get("(en)", ""):
            errors.append("app/(en)/layout.tsx must declare html lang=en")
    dynamic_og = ROOT / "app" / "opengraph-image.tsx"
    if dynamic_og.exists():
        errors.append("app/opengraph-image.tsx must remain absent; /og.png is the canonical social image authority")
    for source_page in sorted((ROOT / "app").rglob("page.tsx")):
        if '"/opengraph-image"' in source_page.read_text(encoding="utf-8"):
            errors.append(f"{source_page.relative_to(ROOT)} still references dynamic /opengraph-image")
    public_og = ROOT / "public" / "og.png"
    live_og = LIVE / "og.png"
    if not public_og.exists():
        errors.append("public/og.png is required for Next social-image parity")
    elif public_og.read_bytes() != live_og.read_bytes():
        errors.append("public/og.png must be byte-identical to deploy/live/og.png")

    for family_source in (source_page_for("/family"), source_page_for("/en/family")):
        family_text = family_source.read_text(encoding="utf-8")
        if 'themeColor: "#2b0a1c"' not in family_text:
            errors.append(f"{family_source.relative_to(ROOT)} must declare family theme color #2b0a1c")
    file_icon = ROOT / "app" / "icon.svg"
    if file_icon.exists():
        errors.append("app/icon.svg must remain absent; /favicon.svg is the canonical icon authority")
    public_favicon = ROOT / "public" / "favicon.svg"
    live_favicon = LIVE / "favicon.svg"
    if not public_favicon.exists():
        errors.append("public/favicon.svg is required for Next favicon parity")
    elif public_favicon.read_bytes() != live_favicon.read_bytes():
        errors.append("public/favicon.svg must be byte-identical to deploy/live/favicon.svg")
    for icon_name in ("favicon.ico", "apple-touch-icon.png"):
        public_icon = ROOT / "public" / icon_name
        live_icon = LIVE / icon_name
        if not public_icon.exists() or not live_icon.exists():
            errors.append(f"{icon_name} must exist in public and deploy/live")
            continue
        if public_icon.read_bytes() != live_icon.read_bytes():
            errors.append(f"public/{icon_name} must be byte-identical to deploy/live/{icon_name}")
    apple = LIVE / "apple-touch-icon.png"
    if apple.exists():
        raw = apple.read_bytes()
        if not raw.startswith(b"\x89PNG\r\n\x1a\n") or len(raw) < 24:
            errors.append("apple-touch-icon.png must decode as PNG")
        else:
            width = int.from_bytes(raw[16:20], "big")
            height = int.from_bytes(raw[20:24], "big")
            if (width, height) != (180, 180):
                errors.append(f"apple-touch-icon.png dimensions {(width,height)} != (180,180)")
    ico = LIVE / "favicon.ico"
    if ico.exists():
        raw = ico.read_bytes()
        if len(raw) < 6 or raw[:4] != b"\x00\x00\x01\x00" or int.from_bytes(raw[4:6], "little") < 1:
            errors.append("favicon.ico must decode as ICO")

    public_manifest = ROOT / "public" / "site.webmanifest"
    live_manifest = LIVE / "site.webmanifest"
    if not public_manifest.exists():
        errors.append("public/site.webmanifest is required for Next manifest parity")
    elif public_manifest.read_bytes() != live_manifest.read_bytes():
        errors.append("public/site.webmanifest must be byte-identical to deploy/live/site.webmanifest")
    if public_manifest.exists() and live_manifest.exists():
        try:
            import json
            manifest_data = json.loads(live_manifest.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"site.webmanifest invalid JSON: {exc}")
        else:
            expected_icons = [
                {"src": "/favicon.svg", "sizes": "any", "type": "image/svg+xml"},
                {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
                {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"},
            ]
            if manifest_data.get("icons") != expected_icons:
                errors.append(f"site.webmanifest installability icons drift: {manifest_data.get('icons')!r}")
            if manifest_data.get("background_color") != "#0b0d10":
                errors.append(f"site.webmanifest background_color {manifest_data.get('background_color')!r} != '#0b0d10'")
            if manifest_data.get("theme_color") != "#0b0d10":
                errors.append(f"site.webmanifest theme_color {manifest_data.get('theme_color')!r} != '#0b0d10'")
            for icon_name, expected_size in (("icon-192.png", 192), ("icon-512.png", 512)):
                public_icon = ROOT / "public" / icon_name
                live_icon = LIVE / icon_name
                if not public_icon.exists() or not live_icon.exists():
                    errors.append(f"{icon_name} must exist in public and deploy/live")
                    continue
                if public_icon.read_bytes() != live_icon.read_bytes():
                    errors.append(f"public/{icon_name} must be byte-identical to deploy/live/{icon_name}")
                raw = live_icon.read_bytes()
                if not raw.startswith(b"\x89PNG\r\n\x1a\n") or len(raw) < 24:
                    errors.append(f"{icon_name} must decode as PNG")
                else:
                    width = int.from_bytes(raw[16:20], "big")
                    height = int.from_bytes(raw[20:24], "big")
                    if (width, height) != (expected_size, expected_size):
                        errors.append(f"{icon_name} dimensions {(width,height)} != {(expected_size,expected_size)}")

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
            source = source_page_for(route).read_text(encoding="utf-8")
            marker = f'title: {{ absolute: "{expected_title}" }}'
            if marker not in source:
                fail(errors, route, "source absolute title contract missing")
        if not (15 <= len(title) <= 65):
            fail(errors, route, f"title length {len(title)} outside 15..65")
        if route in DESCRIPTION_120_155:
            if not (120 <= len(desc) <= 155):
                fail(errors, route, f"description length {len(desc)} outside contracted 120..155")
        elif not (50 <= len(desc) <= 160):
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
        favicon_ico = [link for link in parser.links if "icon" in set(link.get("rel", "").lower().split()) and link.get("href") == "/favicon.ico"]
        apple_icon = [link for link in parser.links if "apple-touch-icon" in set(link.get("rel", "").lower().split()) and link.get("href") == "/apple-touch-icon.png"]
        if len(favicon_ico) != 1:
            fail(errors, route, f"favicon.ico link count {len(favicon_ico)} != 1")
        if len(apple_icon) != 1 or apple_icon[0].get("sizes") != "180x180":
            fail(errors, route, "apple-touch-icon 180x180 link missing")

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
    public_html_paths = [path for path in pages if route_for(path) != "/404"]
    latest_html_date = latest_public_html_commit_date(public_html_paths, errors)
    if expected_lastmod and latest_html_date is not None:
        source_lastmod_date = date.fromisoformat(expected_lastmod)
        if source_lastmod_date < latest_html_date:
            errors.append(
                f"sitemap lastmod {expected_lastmod} older than latest public HTML commit {latest_html_date.isoformat()}"
            )
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

    freshness = latest_html_date.isoformat() if latest_html_date is not None else "SKIPPED_SHALLOW"
    print(
        f"SEARCH_METADATA_PASS pages={checked} public_routes={len(public_routes)} "
        f"sitemap={len(sitemap_urls)} freshness={freshness}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
