#!/usr/bin/env python3
from __future__ import annotations
from guide_route_admission import admitted_route_count, require_public_html, require_canonical_urls

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy" / "live"
PUBLIC = ROOT / "public"
ASSET = "robert-dumanyan-mentor.webp"
ASSET_SHA256 = "1ccb8e47747706274a47302ed1a379748269de24890b5778ab721fd62ff8251b"
GITHUB = "https://github.com/bitmaster162"
LINKEDIN = "https://www.linkedin.com/in/robert-dumanyan-984171335/"
errors: list[str] = []
checks = 0

TARGETS = {
    "index.html": "ru",
    "en.html": "en",
    "about.html": "ru",
    "en/about.html": "en",
}
EXPECTED = {
    "ru": {
        "eyebrow": "НАСТАВНИК · HUMAN IN THE LOOP",
        "name": "Роберт Думанян",
        "role": "Основатель / преподаватель",
        "summary": "Работает с AI-системами, research workflows, агентами, автоматизацией, decision workflows и цифровыми продуктами. На занятиях: цель → спецификация → сборка → проверка → результат.",
        "alt": "Роберт Думанян — основатель и преподаватель AI Skill Lab",
    },
    "en": {
        "eyebrow": "MENTOR · HUMAN IN THE LOOP",
        "name": "Robert Dumanyan",
        "role": "Founder / instructor",
        "summary": "Works with AI systems, research workflows, agents, automation, decision workflows and digital products. Sessions follow the same discipline: goal → specification → build → verification → output.",
        "alt": "Robert Dumanyan — founder and instructor at AI Skill Lab",
    },
}
FOCUS = ["AI systems", "Research workflows", "AI agents", "Automation", "Decision workflows", "Digital products"]
RELEASE = json.loads((LIVE / "_release.json").read_text(encoding="utf-8")).get("release_id")
E32 = RELEASE  in {'E3_2_RU_GLOSSARY_R1','E3_4_AI_SAFETY_AUDIENCE_R1','E3_5_HEADING_STRUCTURE_R1'}
RU_FOCUS_E32 = ["ИИ-системы", "Исследовательские процессы", "ИИ-агенты", "Автоматизация", "Процессы принятия решений", "Цифровые продукты"]
if E32:
    EXPECTED["ru"]["eyebrow"] = "НАСТАВНИК · ПРОВЕРКА ЧЕЛОВЕКОМ"
    EXPECTED["ru"]["summary"] = ("Работает с ИИ-системами, исследовательскими процессами, агентами, "
                                 "автоматизацией, процессами принятия решений и цифровыми продуктами. "
                                 "На занятиях: цель → спецификация → сборка → проверка → результат.")

def req(cond: bool, message: str) -> None:
    global checks
    checks += 1
    if not cond:
        errors.append(message)

for label, path in [("public", PUBLIC / ASSET), ("deploy", LIVE / ASSET)]:
    req(path.is_file(), f"{label} mentor asset missing")
    if path.is_file():
        data = path.read_bytes()
        req(hashlib.sha256(data).hexdigest() == ASSET_SHA256, f"{label} mentor asset SHA drift")
        req(len(data) <= 12_000, f"{label} mentor asset too large: {len(data)}")
if (PUBLIC / ASSET).is_file() and (LIVE / ASSET).is_file():
    req((PUBLIC / ASSET).read_bytes() == (LIVE / ASSET).read_bytes(), "public/deploy mentor asset mismatch")

mentor_source = (ROOT / "lib" / "mentor.ts").read_text(encoding="utf-8")
for marker in [
    'image: "/robert-dumanyan-mentor.webp"',
    'name: { ru: "Роберт Думанян", en: "Robert Dumanyan" }',
    'role: { ru: "Основатель / преподаватель", en: "Founder / instructor" }',
    GITHUB,
    LINKEDIN,
] + FOCUS:
    req(marker in mentor_source, f"mentor source missing {marker!r}")

card_source = (ROOT / "components" / "workshop" / "MentorCard.tsx").read_text(encoding="utf-8")
for marker in [
    'data-a5-mentor="true"',
    "mentorProfile.image",
    "mentorProfile.name[locale]",
    "mentorProfile.role[locale]",
    "mentorProfile.summary[locale]",
    "mentorProfile.github",
    "mentorProfile.linkedin",
    'target="_blank"',
    'rel="noopener noreferrer"',
]:
    req(marker in card_source, f"MentorCard missing {marker!r}")
req("mentorProfile.calcom" not in card_source, "MentorCard must not add Cal.com")
req("mentorProfile.bitevo" not in card_source, "MentorCard must not add BitEvo")

home_source = (ROOT / "components" / "workshop" / "WorkshopHome.tsx").read_text(encoding="utf-8")
req('import { MentorCard } from "./MentorCard";' in home_source, "WorkshopHome mentor import missing")
req(home_source.count("<MentorCard locale={locale}/>") == 1, "WorkshopHome mentor mount count")

for rel, locale in [
    ("app/(ru)/about/page.tsx", "ru"),
    ("app/(en)/en/about/page.tsx", "en"),
]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    req('import { MentorCard } from "@/components/workshop/MentorCard";' in text, f"{rel}: MentorCard import")
    req(text.count(f'<MentorCard locale="{locale}"/>') == 1, f"{rel}: MentorCard mount")

structured = (ROOT / "lib" / "structured-data.ts").read_text(encoding="utf-8")
for marker in [
    'import { mentorProfile } from "@/lib/mentor";',
    "name: mentorProfile.name.en",
    "jobTitle: mentorProfile.role.en",
    "mentorProfile.image",
    "mentorProfile.github",
    "mentorProfile.linkedin",
]:
    req(marker in structured, f"structured data source missing {marker!r}")

for rel, locale in TARGETS.items():
    text = (LIVE / rel).read_text(encoding="utf-8")
    req(text.count('data-a5-mentor="true"') == 1, f"{rel}: mentor block count")
    m = re.search(r'<section class="mentorSection" data-a5-mentor="true">([\s\S]*?)</section>', text)
    req(m is not None, f"{rel}: mentor block parse")
    if not m:
        continue
    block = m.group(1)
    exp = EXPECTED[locale]
    for value in [exp["eyebrow"], exp["name"], exp["role"], exp["summary"], exp["alt"]]:
        req(value in block, f"{rel}: missing mentor value {value!r}")
    for item in (RU_FOCUS_E32 if E32 and locale == "ru" else FOCUS):
        req(block.count(f"<span>{item}</span>") == 1, f"{rel}: focus {item}")
    req(block.count(f'href="{GITHUB}"') == 1, f"{rel}: GitHub link")
    req(block.count(f'href="{LINKEDIN}"') == 1, f"{rel}: LinkedIn link")
    req(block.count('target="_blank" rel="noopener noreferrer"') == 2, f"{rel}: external-link hardening")
    req(block.count(f'src="/{ASSET}"') == 1, f"{rel}: mentor image")
    req('width="192" height="192"' in block, f"{rel}: image dimensions")
    req("<form" not in block.lower(), f"{rel}: mentor block must not contain form")
    req("<script" not in block.lower(), f"{rel}: mentor block must not contain script")
    req("cal.com" not in block and "bitevo.work" not in block, f"{rel}: unapproved extra mentor links")

for rel in ["about.html", "en/about.html"]:
    text = (LIVE / rel).read_text(encoding="utf-8")
    people = []
    for body in re.findall(r'<script type="application/ld\+json">([\s\S]*?)</script>', text):
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("@type") == "Person":
            people.append(data)
    req(len(people) == 1, f"{rel}: Person JSON-LD count={len(people)}")
    if len(people) == 1:
        person = people[0]
        req(person.get("name") == "Robert Dumanyan", f"{rel}: Person name")
        req(person.get("jobTitle") == "Founder / instructor", f"{rel}: Person jobTitle")
        req(person.get("image") == f"https://aiskillab.work/{ASSET}", f"{rel}: Person image")
        req(person.get("sameAs") == ["https://t.me/BiTFormer", GITHUB, LINKEDIN], f"{rel}: Person sameAs")
        req(person.get("knowsAbout") == FOCUS, f"{rel}: Person knowsAbout")

for rel in ["kids.html", "en/kids.html", "pricing.html", "en/pricing.html", "start.html", "en/start.html"]:
    req('data-a5-mentor="true"' not in (LIVE / rel).read_text(encoding="utf-8"), f"{rel}: A5 card leaked")

source_css = (ROOT / "components" / "workshop" / "WorkshopShell.module.css").read_text(encoding="utf-8")
static_css = (LIVE / "workshop.css").read_text(encoding="utf-8")
for label, css in [("source", source_css), ("static", static_css)]:
    for marker in [".mentorSection", ".mentorCard", ".mentorPhoto", ".mentorLinks", "@media(max-width:620px)"]:
        req(marker in css, f"{label} CSS missing {marker}")
    start = css.rfind("A5")
    block = css[start:] if start >= 0 else ""
    req("font-size:" not in block, f"{label} A5 must not override typography size scale")

public = [p for p in LIVE.rglob("*.html") if p.name != "404.html"]
require_public_html(LIVE)
req(len(public) == admitted_route_count(), f"public route count {len(public)} != {admitted_route_count()}")

builder = (ROOT / "scripts" / "build_a5_mentor.py").read_text(encoding="utf-8")
for marker in ["A5_MENTOR_BUILD_PASS", ASSET_SHA256, "https://cal.com/robert-dumanyan-vlck0x", "6fbefde3096a05011dcbc911a5539253500389c9a63a330acf4503b039722418", "A5_MENTOR_START", 'data-a5-mentor="true"']:
    req(marker in builder, f"builder missing {marker!r}")

print(f"A5_MENTOR_CHECK checks={checks} pages=4 person_jsonld=2 focus=6 asset_bytes={(PUBLIC/ASSET).stat().st_size if (PUBLIC/ASSET).exists() else 0} public_routes={len(public)}")
if errors:
    print("A5_MENTOR_FAIL")
    for error in errors:
        print("-", error)
    sys.exit(1)
print("A5_MENTOR_PASS")
