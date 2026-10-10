#!/usr/bin/env python3
from __future__ import annotations
from guide_route_admission import admitted_route_count, require_public_html, require_route_set, require_canonical_urls

import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy" / "live"
ORIGIN = "https://aiskillab.work"

EXPECTED_MD = {
    "guides/aiskillab/ai-safety-for-kids.ru.md": "6f912d320a3338855e3d951f2c44e7979319bb774409b4f644a68097ee9afa07",
    "guides/aiskillab/ai-safety-for-kids.en.md": "a8f009ef579ff061c28f969e1a51b6d28c61c8cc5d2876e80ea4fe88f805c4c2",
}
LISTING = {
    "/guides": ("Гайды", "Короткие проверенные материалы для родителей, взрослых учеников и команд. У каждого — дата проверки и источники."),
    "/en/guides": ("Guides", "Short, checked guides for parents, adult learners and teams. Each one shows when it was checked and its sources."),
}
ARTICLES = {
    "/guides/ai-safety-for-kids": {
        "alternate": "/en/guides/ai-safety-for-kids",
        "title": "AI и ребёнок 8–13: чек-лист безопасности для родителей",
        "crosslink": "Чек-лист для родителей: возраст, данные, родительский контроль →",
        "sources": 8,
    },
    "/en/guides/ai-safety-for-kids": {
        "alternate": "/guides/ai-safety-for-kids",
        "title": "AI and your child (8–13): a safety checklist for parents",
        "crosslink": "Parent checklist: age rules, data, parental controls →",
        "sources": 8,
    },
}
CROSSLINK_ROUTES = {
    "/kids": "/guides/ai-safety-for-kids",
    "/parents": "/guides/ai-safety-for-kids",
    "/safety": "/guides/ai-safety-for-kids",
    "/en/kids": "/en/guides/ai-safety-for-kids",
    "/en/parents": "/en/guides/ai-safety-for-kids",
    "/en/safety": "/en/guides/ai-safety-for-kids",
}


RELEASE = json.loads((LIVE / "_release.json").read_text(encoding="utf-8")).get("release_id")
if RELEASE in {"E3_1_RU_SEO_R1","E3_3_H1_ACTION_R1","E3_2_RU_GLOSSARY_R1","E3_4_AI_SAFETY_AUDIENCE_R1","E3_5_HEADING_STRUCTURE_R1",'E3_6_WORKSHOP_HERO_PANEL_R1'}:
    EXPECTED_MD["guides/aiskillab/ai-safety-for-kids.ru.md"] = "f8be315623ddcfb8b3e3f5da46a52305f943df3aecb6ea2915895d2ed6aff75e"
    LISTING["/guides"] = ("Гайды", "Короткие проверенные материалы об ИИ для родителей, взрослых учеников и команд. У каждого — дата проверки и источники.")
    ARTICLES["/guides/ai-safety-for-kids"]["title"] = "ИИ и ребёнок 8–13: чек-лист безопасности для родителей"

def route_for(path: Path) -> str:
    rel = path.relative_to(LIVE).as_posix()
    if rel == "index.html":
        return "/"
    if rel == "en.html":
        return "/en"
    return "/" + rel[:-5]


def file_for(route: str) -> Path:
    if route == "/":
        return LIVE / "index.html"
    if route == "/en":
        return LIVE / "en.html"
    return LIVE / f"{route.lstrip('/')}.html"


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


class JsonLdParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.capture = False
        self.buffer: list[str] = []
        self.blocks: list[dict] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        values = dict(attrs)
        if tag == "script" and values.get("type") == "application/ld+json":
            self.capture = True
            self.buffer = []

    def handle_data(self, data: str) -> None:
        if self.capture:
            self.buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self.capture:
            raw = "".join(self.buffer)
            try:
                value = json.loads(raw)
                if isinstance(value, dict):
                    self.blocks.append(value)
                elif isinstance(value, list):
                    self.blocks.extend(x for x in value if isinstance(x, dict))
            finally:
                self.capture = False
                self.buffer = []


def main() -> int:
    errors: list[str] = []
    checks = 0

    # Attached E2 guide copy must remain byte-exact.
    for rel, expected in EXPECTED_MD.items():
        path = ROOT / rel
        checks += 2
        require(path.is_file(), f"missing source guide {rel}", errors)
        if path.is_file():
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            require(actual == expected, f"{rel}: source text changed sha={actual}", errors)

    public = [p for p in LIVE.rglob("*.html") if p.name != "404.html"]
    routes = {route_for(p) for p in public}
    checks += 3
    require_route_set(routes, "E2 guide public routes")
    require("/guides" in routes and "/en/guides" in routes, "guide listings missing from route authority", errors)
    require(set(ARTICLES).issubset(routes), "guide article routes missing", errors)

    sitemap = (LIVE / "sitemap.xml").read_text(encoding="utf-8")
    sitemap_urls_raw = re.findall(r"<loc>(https?://[^<]+)</loc>", sitemap)
    require_canonical_urls(sitemap_urls_raw, "E2 sitemap URLs")
    sitemap_urls = set(sitemap_urls_raw)
    expected_urls = {ORIGIN + ("/" if route == "/" else route) for route in routes}
    checks += 2
    require(sitemap_urls == expected_urls, f"sitemap route mismatch missing={sorted(expected_urls-sitemap_urls)} extra={sorted(sitemap_urls-expected_urls)}", errors)
    require(len(sitemap_urls) == admitted_route_count(), f"sitemap URL count {len(sitemap_urls)} != {admitted_route_count()}", errors)

    llms = (LIVE / "llms.txt").read_text(encoding="utf-8")
    llms_urls = re.findall(r"\]\((https?://[^)]+)\)", llms)
    checks += 3
    require("## Guides" in llms, "llms.txt missing Guides section", errors)
    require_canonical_urls(llms_urls, "E2 llms URLs")
    require(set(llms_urls) == expected_urls, "llms.txt/sitemap parity mismatch", errors)

    # Footer link belongs to every public Workshop page.
    for page in public:
        route = route_for(page)
        raw = page.read_text(encoding="utf-8")
        en = route == "/en" or route.startswith("/en/")
        anchor = '<a href="/en/guides">Guides</a>' if en else '<a href="/guides">Гайды</a>'
        checks += 1
        require(anchor in raw, f"{route}: Guides footer link missing", errors)

    # Listing contract.
    for route, (title, subtitle) in LISTING.items():
        raw = file_for(route).read_text(encoding="utf-8")
        checks += 7
        require(f"<h1>{title}</h1>" in raw, f"{route}: listing H1 drift", errors)
        require(subtitle in raw, f"{route}: listing subtitle drift", errors)
        require('class="guideCard"' in raw, f"{route}: guide card missing", errors)
        require('href="/guides/ai-safety-for-kids"' in raw if route == "/guides" else 'href="/en/guides/ai-safety-for-kids"' in raw, f"{route}: first guide link missing", errors)
        require(f'<link rel="canonical" href="{ORIGIN}{route}">' in raw, f"{route}: canonical missing", errors)
        require('hreflang="x-default"' in raw, f"{route}: x-default missing", errors)
        require('content="https://aiskillab.work/og.png"' in raw, f"{route}: OG PNG missing", errors)

    # Article contract.
    for route, expected in ARTICLES.items():
        raw = file_for(route).read_text(encoding="utf-8")
        parser = JsonLdParser()
        parser.feed(raw)
        types = [x.get("@type") for x in parser.blocks]
        external_source_links = re.findall(r'<a href="(https?://[^"]+)" target="_blank" rel="noopener">', raw)
        source_urls = [url for url in external_source_links if any(host in urlparse(url).netloc for host in [
            "help.openai.com", "support.google.com", "anthropic.com", "suno.com", "replit.com", "docs.github.com", "internetmatters.org"
        ])]
        checks += 16
        require(f"<h1>{expected['title']}</h1>" in raw, f"{route}: article H1 drift", errors)
        require('class="guideToc"' in raw and 'href="#section-1"' in raw and 'href="#sources"' in raw, f"{route}: TOC/anchors missing", errors)
        require('class="guideTableWrap"><table>' in raw, f"{route}: semantic table wrapper missing", errors)
        require(raw.count("<table>") == 1, f"{route}: expected exactly one table", errors)
        require('overflow-x:auto' in (LIVE / "workshop.css").read_text(encoding="utf-8"), "guide table overflow rule missing", errors)
        require(f'<link rel="canonical" href="{ORIGIN}{route}">' in raw, f"{route}: canonical missing", errors)
        ru = route if not route.startswith("/en/") else expected["alternate"]
        en = route if route.startswith("/en/") else expected["alternate"]
        require(f'hreflang="ru" href="{ORIGIN}{ru}"' in raw, f"{route}: RU hreflang drift", errors)
        require(f'hreflang="en" href="{ORIGIN}{en}"' in raw, f"{route}: EN hreflang drift", errors)
        require(f'hreflang="x-default" href="{ORIGIN}{ru}"' in raw, f"{route}: x-default drift", errors)
        require("Article" in types, f"{route}: Article JSON-LD missing", errors)
        require("BreadcrumbList" in types, f"{route}: BreadcrumbList JSON-LD missing", errors)
        require('content="article"' in raw, f"{route}: og:type article missing", errors)
        require('content="https://aiskillab.work/og.png"' in raw, f"{route}: OG PNG missing", errors)
        require("guideReviewMeta" in raw, f"{route}: reviewed/next review line missing", errors)
        require(len(set(source_urls)) == expected["sources"], f"{route}: external source count {len(set(source_urls))} != {expected['sources']}", errors)
        require('rel="noopener"' in raw, f"{route}: external noopener missing", errors)

    # Required contextual links from youth/safety pages.
    for route, href in CROSSLINK_ROUTES.items():
        raw = file_for(route).read_text(encoding="utf-8")
        checks += 2
        require('data-guide-crosslink="e2"' in raw, f"{route}: static E2 crosslink marker missing", errors)
        require(f'href="{href}"' in raw, f"{route}: static guide crosslink missing", errors)

    # Source-side reusable pipeline and links.
    source_markers = {
        "lib/guides.ts": ["listGuides", "renderGuideMarkdown", "guides", "aiskillab"],
        "components/guides/GuidePages.tsx": ["GuideListing", "GuideArticle", "BreadcrumbList", "Article"],
        "app/(ru)/guides/page.tsx": ['listGuides("ru")'],
        "app/(en)/en/guides/page.tsx": ['listGuides("en")'],
        "app/(ru)/guides/[slug]/page.tsx": ['generateStaticParams', 'getGuide("ru"'],
        "app/(en)/en/guides/[slug]/page.tsx": ['generateStaticParams', 'getGuide("en"'],
        "app/sitemap.ts": ['listGuides("ru")', 'listGuides("en")', '"/guides"', '"/en/guides"'],
        "components/workshop/WorkshopShell.tsx": ['"/en/guides" : "/guides"', '"Guides" : "Гайды"'],
        "components/workshop/WorkshopAudience.tsx": ['guides/ai-safety-for-kids', 'Parent checklist: age rules, data, parental controls', 'Чек-лист для родителей: возраст, данные, родительский контроль'],
        "app/(ru)/parents/page.tsx": ['href="/guides/ai-safety-for-kids"'],
        "app/(en)/en/parents/page.tsx": ['href="/en/guides/ai-safety-for-kids"'],
        "app/(ru)/safety/page.tsx": ['href="/guides/ai-safety-for-kids"'],
        "app/(en)/en/safety/page.tsx": ['href="/en/guides/ai-safety-for-kids"'],
    }
    for rel, markers in source_markers.items():
        path = ROOT / rel
        checks += 1 + len(markers)
        require(path.is_file(), f"missing source file {rel}", errors)
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            for marker in markers:
                require(marker in text, f"{rel}: missing marker {marker}", errors)

    css = (LIVE / "workshop.css").read_text(encoding="utf-8")
    checks += 5
    require("/* E2_GUIDES_START */" in css and "/* E2_GUIDES_END */" in css, "static guide CSS block missing", errors)
    require(".guideBody{font-size:1.02rem;line-height:1.58;max-width:66ch" in css, "guide line width/height contract missing", errors)
    require(".guideTableWrap{overflow-x:auto;max-width:100%" in css, "table-only horizontal scroll contract missing", errors)
    require("@media(max-width:640px)" in css, "guide mobile rule missing", errors)
    require("min-width:680px" in css, "guide table minimum width missing", errors)

    print(f"E2_GUIDES_CHECK checks={checks} public_routes={len(routes)} sitemap={len(sitemap_urls)} llms={len(llms_urls)} source_guides={len(EXPECTED_MD)}")
    if errors:
        print("E2_GUIDES_FAIL")
        for error in errors:
            print("-", error)
        return 1
    print("E2_GUIDES_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
