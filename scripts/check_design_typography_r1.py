#!/usr/bin/env python3
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE_CSS = ROOT / "components" / "workshop" / "WorkshopShell.module.css"
STATIC_CSS = ROOT / "deploy" / "live" / "workshop.css"
LIVE = ROOT / "deploy" / "live"

SOURCE_MARKERS = [
    "/* DESIGN_TYPOGRAPHY_R1 · Design System 2026-10-01.",
    ".hero h1{font-size:clamp(34px,calc(21.73px + 3.146vw),62px);line-height:1.03}",
    ".startHero h1,.audienceHero h1,.familyHero h1{font-size:clamp(31px,calc(21.80px + 2.360vw),52px);line-height:1.03}",
    ".pricingHero h1{font-size:clamp(28px,calc(24.49px + .899vw),36px);line-height:1.05}",
    ".sectionHead h2,.darkBand h2,.finalCta h2,.proofBand h2{font-size:clamp(24px,calc(17.87px + 1.573vw),38px);line-height:1.08}",
    ".page :global(.hero h1),.page :global(.proofHero h1),.page :global(.projectStudioHero h1){font-size:clamp(31px,calc(21.80px + 2.360vw),52px);line-height:1.03}",
    ".page :global(.sectionHead h2){font-size:clamp(24px,calc(17.87px + 1.573vw),38px);line-height:1.08}",
]

STATIC_MARKERS = [
    "/* DESIGN_TYPOGRAPHY_R1 · Design System 2026-10-01.",
    ".workshopPage main .workshopHero h1{font-size:clamp(34px,calc(21.73px + 3.146vw),62px);line-height:1.03}",
    ".workshopPage main :is(.hero,.proofHero,.projectStudioHero,.startHero,.audienceHero,.familyHero) h1{font-size:clamp(31px,calc(21.80px + 2.360vw),52px);line-height:1.03}",
    ".workshopPage main .pricingHero h1{font-size:clamp(28px,calc(24.49px + .899vw),36px);line-height:1.05}",
    ".workshopPage main :is(.sectionHead,.darkBand,.finalCta,.proofBand) h2{font-size:clamp(24px,calc(17.87px + 1.573vw),38px);line-height:1.08}",
]

PAGES = [
    "about", "build", "business", "challenge", "curriculum", "family", "faq",
    "home", "kids", "matcher", "method", "parents", "personal", "phuket",
    "pricing", "privacy", "projects", "proof", "safety", "start", "studio",
    "teens", "terms",
]

ROLE_CLASSES = {
    "home": {"workshopHero"},
    "pricing": {"pricingHero"},
    "internal": {"hero", "proofHero", "projectStudioHero", "startHero", "audienceHero", "familyHero"},
}

def route_file(slug: str, en: bool) -> Path:
    if slug == "home":
        return LIVE / ("en.html" if en else "index.html")
    return LIVE / ("en" if en else "") / f"{slug}.html" if en else LIVE / f"{slug}.html"

class FirstH1RoleParser(HTMLParser):
    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, set[str]]] = []
        self.role = "missing"
        self.found = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        classes = set((attr_map.get("class") or "").split())
        if tag == "h1" and not self.found:
            inherited = set(classes)
            for _, ancestor_classes in self.stack:
                inherited.update(ancestor_classes)
            if inherited & ROLE_CLASSES["home"]:
                self.role = "home"
            elif inherited & ROLE_CLASSES["pricing"]:
                self.role = "pricing"
            elif inherited & ROLE_CLASSES["internal"]:
                self.role = "internal"
            else:
                self.role = "unclassified"
            self.found = True
        if tag not in self.VOID_TAGS:
            self.stack.append((tag, classes))

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break


def h1_role(path: Path) -> str:
    parser = FirstH1RoleParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser.role

def main() -> int:
    errors: list[str] = []
    checks = 0
    source = SOURCE_CSS.read_text(encoding="utf-8")
    static = STATIC_CSS.read_text(encoding="utf-8")

    for marker in SOURCE_MARKERS:
        checks += 1
        if source.count(marker) != 1:
            errors.append(f"source marker count != 1: {marker[:90]}")
    for marker in STATIC_MARKERS:
        checks += 1
        if static.count(marker) != 1:
            errors.append(f"static marker count != 1: {marker[:90]}")

    checks += 2
    if "guideListingHero" in "\n".join(STATIC_MARKERS):
        errors.append("static design typography selectors must not include guideListingHero")
    if "guideListingHero" in "\n".join(SOURCE_MARKERS):
        errors.append("source design typography selectors must not include guideListingHero")

    counts = {"home": 0, "pricing": 0, "internal": 0}
    for en in (False, True):
        for slug in PAGES:
            path = route_file(slug, en)
            checks += 1
            if not path.is_file():
                errors.append(f"missing route file: {path.relative_to(ROOT)}")
                continue
            role = h1_role(path)
            expected = "home" if slug == "home" else "pricing" if slug == "pricing" else "internal"
            if role != expected:
                errors.append(f"{path.relative_to(ROOT)} role={role} expected={expected}")
            else:
                counts[role] += 1

    for guide in (LIVE / "guides.html", LIVE / "en" / "guides.html"):
        checks += 1
        if not guide.is_file():
            errors.append(f"missing guide route: {guide.relative_to(ROOT)}")
            continue
        if h1_role(guide) != "unclassified":
            errors.append(f"guides unexpectedly classified into design-package role: {guide.relative_to(ROOT)}")

    print(
        f"DESIGN_TYPOGRAPHY_R1_CHECK checks={checks} routes=46 "
        f"home={counts['home']} internal={counts['internal']} pricing={counts['pricing']} guides_excluded=2"
    )
    if errors:
        print("DESIGN_TYPOGRAPHY_R1_FAIL")
        for error in errors:
            print("-", error)
        return 1
    print("DESIGN_TYPOGRAPHY_R1_PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
