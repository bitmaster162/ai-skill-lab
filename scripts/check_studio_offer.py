#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
E32 = json.loads((ROOT / "deploy/live/_release.json").read_text(encoding="utf-8")).get("release_id")  in {'E3_2_RU_GLOSSARY_R1','E3_4_AI_SAFETY_AUDIENCE_R1','E3_5_HEADING_STRUCTURE_R1'}
errors = []
checks = 0

def source_path(rel: str) -> Path:
    grouped = (ROOT / "app" / "(ru)" / "layout.tsx").exists() and (ROOT / "app" / "(en)" / "layout.tsx").exists()
    if not grouped:
        return ROOT / rel
    if rel.startswith("app/en/"):
        return ROOT / ("app/(en)/en/" + rel.removeprefix("app/en/"))
    if rel.startswith("app/"):
        return ROOT / ("app/(ru)/" + rel.removeprefix("app/"))
    return ROOT / rel

studio_surfaces = [
    ("app/studio/page.tsx", False),
    ("app/en/studio/page.tsx", True),
    ("deploy/live/studio.html", False),
    ("deploy/live/en/studio.html", True),
]
common = [
    "AI STUDIO / BUILD WITH US",
    "CUSTOM SCOPE",
    "AI PRODUCT / WEBSITE",
    "RESEARCH / DECISION",
    "AUTOMATION / AGENT",
    "TEAM ENABLEMENT",
    "DIAGNOSE",
    "SCOPE",
    "BUILD",
    "VERIFY",
    "SHIP",
    "TRANSFER",
    "Ship / Revise / Stop",
    "/build",
]

E32_STUDIO = {
    "AI STUDIO / BUILD WITH US": "СТУДИЯ / СОБИРАЕМ ВМЕСТЕ",
    "CUSTOM SCOPE": "ОБЪЁМ РАБОТ",
    "AI PRODUCT / WEBSITE": "ИИ-ПРОДУКТ / САЙТ",
    "RESEARCH / DECISION": "ИССЛЕДОВАНИЕ / РЕШЕНИЕ",
    "AUTOMATION / AGENT": "АВТОМАТИЗАЦИЯ / АГЕНТ",
    "TEAM ENABLEMENT": "ОБУЧЕНИЕ КОМАНДЫ",
    "DIAGNOSE": "ДИАГНОСТИКА", "SCOPE": "ОБЪЁМ РАБОТ",
    "BUILD": "СБОРКА", "VERIFY": "ПРОВЕРКА", "SHIP": "ЗАПУСК",
    "TRANSFER": "ПЕРЕДАЧА",
    "Ship / Revise / Stop": "выпустить, доработать или остановить",
}
for rel, en in studio_surfaces:
    text = source_path(rel).read_text(encoding="utf-8")
    for marker in common:
        checks += 1
        required = E32_STUDIO.get(marker, marker) if E32 and not en else marker
        if required.casefold() not in text.casefold():
            errors.append(f"{rel}: missing {required}")
    checks += 1
    if re.search(r"\$\s?[0-9]", text):
        errors.append(f"{rel}: AI Studio must remain custom-scope, found hard-coded price")
    start_route = "/en/start" if en else "/start"
    checks += 1
    if start_route not in text:
        errors.append(f"{rel}: missing Start route {start_route}")
    for anchor in [
        "studio-offers",
        "studio-delivery",
        "studio-fit",
        "studio-claims",
        "studio-brief",
    ]:
        checks += 2
        if f'id="{anchor}"' not in text:
            errors.append(f"{rel}: missing section anchor {anchor}")
        if f'href="#{anchor}"' not in text:
            errors.append(f"{rel}: missing inner-nav link #{anchor}")
    claims = (
        ["guaranteed ROI", "autonomous critical business decision"]
        if en
        else ["гарантированного ROI", "автономного решения критичных бизнес-вопросов"]
    )
    for marker in claims:
        checks += 1
        if marker.casefold() not in text.casefold():
            errors.append(f"{rel}: missing claims boundary {marker}")

mounts = {
    "app/page.tsx": '<WorkshopHome locale="ru" />',
    "app/en/page.tsx": '<WorkshopHome locale="en" />',
}
for rel, marker in mounts.items():
    checks += 1
    if marker not in source_path(rel).read_text(encoding="utf-8"):
        errors.append(f"{rel}: Workshop home mount missing")

component = (ROOT / "components/workshop/WorkshopHome.tsx").read_text(encoding="utf-8")
for marker in [
    "/studio",
    "/en/studio",
    "Открыть Studio →",
    "Open Studio →",
    "Studio для ассистента",
    "Studio for an assistant",
]:
    checks += 1
    required = {"Открыть Studio →":"Открыть студию →","Studio для ассистента":"Студия для ассистента"}.get(marker,marker) if E32 else marker
    if required not in component:
        errors.append(f"components/workshop/WorkshopHome.tsx: missing {required!r}")

static_homes = {
    "deploy/live/index.html": [
        'href="/studio"',
        "Открыть Studio →",
        "Studio для ассистента",
    ],
    "deploy/live/en.html": [
        'href="/en/studio"',
        "Open Studio →",
        "Studio for an assistant",
    ],
}
for rel, markers in static_homes.items():
    text = source_path(rel).read_text(encoding="utf-8")
    if E32 and rel == "deploy/live/index.html":
        markers = [{"Studio для ассистента":"Студия для ассистента","Открыть Studio →":"Открыть студию →"}.get(x,x) for x in markers]
    for marker in markers:
        checks += 1
        if marker not in text:
            errors.append(f"{rel}: missing Studio discoverability {marker!r}")

lab_command = (ROOT / "components/LabCommand.tsx").read_text(encoding="utf-8")
for marker in ["AI Studio", "/studio", "/en/studio", "BUILD WITH US"]:
    checks += 1
    if marker not in lab_command:
        errors.append(f"components/LabCommand.tsx: missing {marker!r}")

static_command = (ROOT / "deploy/live/lab-command.js").read_text(encoding="utf-8")
for marker in ["AI Studio", "b+'/studio'", "BUILD WITH US"]:
    checks += 1
    if marker not in static_command:
        errors.append(f"deploy/live/lab-command.js: missing {marker!r}")

print(
    f"studio_offer_checks={checks} studio_surfaces={len(studio_surfaces)} "
    "discovery_surfaces=7"
)
if errors:
    for error in errors:
        print("FAIL:", error)
    sys.exit(1)
print("AI_STUDIO_OFFER_PASS")
