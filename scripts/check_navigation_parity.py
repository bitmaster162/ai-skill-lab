#!/usr/bin/env python3
from pathlib import Path
import re
import sys
from css_graph import read_local_css_graph

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy" / "live"
errors=[]
checks=0
R77_HOMES={
    "index.html":{"start":"/start","lang":"/en"},
    "en.html":{"start":"/en/start","lang":"/"},
}

for path in sorted(LIVE.rglob("*.html")):
    if path.name == "404.html":
        continue
    rel=path.relative_to(LIVE).as_posix()
    text=path.read_text(encoding="utf-8")
    if rel in R77_HOMES:
        expected=R77_HOMES[rel]
        for marker in ['<header class="header">','class="headerActions"',f'href="{expected["start"]}" class="topCta"',f'href="{expected["lang"]}" class="lang"']:
            checks += 1
            if marker not in text:
                errors.append(f"{rel}: missing R77 home marker {marker}")
        checks += 1
        if '<header class="nav">' in text:
            errors.append(f"{rel}: legacy .nav header must not return")
        continue
    en = rel.startswith("en/")
    route = "/en/" + rel[3:-5] if en else "/" + rel[:-5]
    expected_main = [
        "/en/personal","/en/business","/en/kids","/en/teens","/en/pricing","/en/about","/en/faq"
    ] if en else [
        "/personal","/business","/kids","/teens","/pricing","/about","/faq"
    ]
    header_match=re.search(r'<header class="nav">(.*?)</header>',text,re.S)
    checks += 1
    if not header_match:
        errors.append(f"{rel}: missing .nav header")
        continue
    header=header_match.group(1)
    for marker in ['class="navActions"','class="langSwitch"','class="mobileNav"','<summary aria-label=']:
        checks += 1
        if marker not in header:
            errors.append(f"{rel}: missing {marker}")
    for href in expected_main:
        checks += 2
        # each primary route must appear in desktop + mobile nav
        count=len(re.findall(fr'href="{re.escape(href)}"',header))
        if count != 2:
            errors.append(f"{rel}: primary nav {href} count={count}, expected 2")
    expected_start = "/en/start" if en else "/start"
    on_start = route == expected_start
    if on_start:
        checks += 1
        if header.count('href="https://t.me/BiTFormer"') != 2:
            errors.append(f"{rel}: start header must expose Telegram exactly twice (desktop/mobile CTA)")
    else:
        checks += 2
        if header.count(f'href="{expected_start}"') != 2:
            errors.append(f"{rel}: internal start CTA count mismatch")
        if 't.me/BiTFormer' in header:
            errors.append(f"{rel}: direct Telegram outside start header")
    checks += 1
    if route in expected_main and header.count('aria-current="page"') != 2:
        errors.append(f"{rel}: active primary route must be marked in desktop+mobile nav")

css=read_local_css_graph(LIVE / "style.css", LIVE)
for marker in [".mobileNav{display:none}","min-height:48px","@media(max-width:980px){.links{display:none}.mobileNav{display:block}"]:
    checks += 1
    if marker not in css:
        errors.append(f"style.css: missing R25 mobile navigation rule {marker}")

if errors:
    print(f"navigation_parity_checks={checks}")
    for e in errors:
        print("FAIL:",e)
    sys.exit(1)
print(f"navigation_parity_checks={checks} legacy_pages=42 r77_homes=2")
print("NAVIGATION_PARITY_PASS")
