#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy" / "live"
errors: list[str] = []
checks = 0

TARGETS = {
    "phuket.html": "ru",
    "en/phuket.html": "en",
}
AREAS = ["Rawai / Nai Harn", "Chalong", "Kata / Karon", "Phuket Town"]
FORMATS = ["LOCAL 1:1", "ONLINE 1:1", "HYBRID"]

def req(cond: bool, message: str) -> None:
    global checks
    checks += 1
    if not cond:
        errors.append(message)

component = ROOT / "components" / "workshop" / "PhuketLocal.tsx"
req(component.is_file(), "missing PhuketLocal.tsx")
if component.is_file():
    source = component.read_text(encoding="utf-8")
    for marker in [
        "data-a4-phuket-local",
        "Real areas, no invented campus.",
        "Реальные районы, без выдуманного кампуса.",
        "not branches or permanent classrooms",
        "не филиалы и не постоянные классы",
        "public classroom address",
        "parent or legal guardian",
    ] + AREAS + FORMATS:
        req(marker in source, f"PhuketLocal source missing {marker!r}")
    req("http://" not in source and "https://" not in source, "PhuketLocal must not add external links")
    req("<form" not in source.lower(), "PhuketLocal must not add form")
    req("fetch(" not in source and "WebSocket(" not in source, "PhuketLocal must not add network primitives")

source_mounts = {
    "app/(ru)/phuket/page.tsx": '<PhuketLocal locale="ru"/>',
    "app/(en)/en/phuket/page.tsx": '<PhuketLocal locale="en"/>',
}
for rel, marker in source_mounts.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    req('import { PhuketLocal } from "@/components/workshop/PhuketLocal";' in text, f"{rel}: import missing")
    req(text.count(marker) == 1, f"{rel}: mount count")

for rel, locale in TARGETS.items():
    text = (LIVE / rel).read_text(encoding="utf-8")
    req(text.count('data-a4-phuket-local="true"') == 1, f"{rel}: local block count")
    req(text.count('data-a4-phuket-formats="true"') == 1, f"{rel}: format block count")
    for area in AREAS:
        req(text.count(f"<strong>{area}</strong>") == 1, f"{rel}: area {area}")
    for fmt in FORMATS:
        req(text.count(f"<span>{fmt}</span>") == 1, f"{rel}: format {fmt}")
    req(text.count('class="phuketAreaGrid"') == 1, f"{rel}: area grid")
    req(text.count('class="phuketFormatGrid"') == 1, f"{rel}: format grid")
    req("permanent school location" in text if locale == "en" else "постоянные классы" in text, f"{rel}: no-campus truth")
    req("<form" not in re.search(r'<section class="phuketLocal"[\s\S]*?</main>', text).group(0).lower(), f"{rel}: no form in A4")
    req("https://" not in re.search(r'<section class="phuketLocal"[\s\S]*?</main>', text).group(0), f"{rel}: no external A4 link")
    req(text.index('data-a4-phuket-local="true"') < text.index("</main>"), f"{rel}: A4 inside main")

# A4 is a two-route content extension, not a route expansion.
public = [p for p in LIVE.rglob("*.html") if p.name != "404.html"]
req(len(public) == 50, f"public route count {len(public)} != 50")
for rel in ["kids.html", "en/kids.html", "personal.html", "en/personal.html", "business.html", "en/business.html"]:
    text = (LIVE / rel).read_text(encoding="utf-8")
    req('data-a4-phuket-local="true"' not in text, f"{rel}: A4 leaked outside Phuket")

source_css = (ROOT / "components" / "workshop" / "WorkshopShell.module.css").read_text(encoding="utf-8")
static_css = (LIVE / "workshop.css").read_text(encoding="utf-8")
for label, css in [("source", source_css), ("static", static_css)]:
    for marker in [".phuketAreaGrid", ".phuketFormatGrid", "@media(max-width:620px)"]:
        req(marker in css, f"{label} CSS missing {marker}")
    block = css[css.rfind("A4"):] if "A4" in css else ""
    req("font-size:" not in block, f"{label} A4 must not override typography size scale")

builder = (ROOT / "scripts" / "build_a4_phuket_local.py").read_text(encoding="utf-8")
for marker in ["A4_PHUKET_BUILD_PASS", 'data-a4-phuket-local="true"', "A4_PHUKET_LOCAL_START"]:
    req(marker in builder, f"builder missing {marker}")

print(f"A4_PHUKET_LOCAL_CHECK checks={checks} pages=2 area_cards=4 areas=6 formats=3 public_routes={len(public)}")
if errors:
    print("A4_PHUKET_LOCAL_FAIL")
    for error in errors:
        print("-", error)
    sys.exit(1)
print("A4_PHUKET_LOCAL_PASS")
