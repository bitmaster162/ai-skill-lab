#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy" / "live"
RELEASE_ID = json.loads((LIVE / "_release.json").read_text(encoding="utf8")).get("release_id")
E32 = RELEASE_ID in {"E3_2_RU_GLOSSARY_R1", "E3_4_AI_SAFETY_AUDIENCE_R1", "E3_5_HEADING_STRUCTURE_R1"}
E34 = RELEASE_ID in {"E3_4_AI_SAFETY_AUDIENCE_R1", "E3_5_HEADING_STRUCTURE_R1"}
errors: list[str] = []
checks = 0

TARGETS = {
    "personal.html": "ru",
    "en/personal.html": "en",
    "teens.html": "ru",
    "en/teens.html": "en",
    "business.html": "ru",
    "en/business.html": "en",
}

SOURCES = [
    "https://replit.com/blog/doubling-down-on-our-commitment-to-secure-vibe-coding",
    "https://www.scworld.com/news/microsoft-365-copilot-zero-click-vulnerability-enabled-data-exfiltration",
    "https://unit42.paloaltonetworks.com/ai-agent-prompt-injection/",
]

EXPECTED = {
    "ru": {
        "eyebrow": "БЕЗОПАСНАЯ РАБОТА С AI-АГЕНТАМИ · 3 КЕЙСА + 5 ПРАВИЛ",
        "heading": "Не доверять плану. Контролировать эффект.",
        "titles": [
            "Replit Agent удалил данные production-базы.",
            "EchoLeak показал, что входящие данные могут стать инструкцией.",
            "Unit 42 увидела hidden prompts на мошеннических страницах.",
        ],
        "rules": [
            "01 · Сначала read-only",
            "02 · Минимальные права",
            "03 · Человек перед необратимым действием",
            "04 · Данные не равны инструкциям",
            "05 · Проверка после эффекта",
        ],
        "distinction": "Кейсы не равнозначны: Replit — реальный операционный инцидент; EchoLeak — подтверждённая уязвимость, исправленная до публичного раскрытия, без известной эксплуатации; кейс Unit 42 — обнаруженная вредоносная попытка prompt injection без подтверждённого успешного обхода deployed ad-review агента.",
    },
    "en": {
        "eyebrow": "SAFE AGENT WORK · 3 CASES + 5 RULES",
        "heading": "Do not trust the plan. Control the effect.",
        "titles": [
            "Replit Agent deleted production-app database data.",
            "EchoLeak showed that incoming data can become an instruction.",
            "Unit 42 found hidden prompts on malicious webpages.",
        ],
        "rules": [
            "01 · Start read-only",
            "02 · Least privilege",
            "03 · Human before irreversible effects",
            "04 · Data is not instruction",
            "05 · Verify after the effect",
        ],
        "distinction": "The cases are not equivalent: Replit was a real operational incident; EchoLeak was a confirmed vulnerability patched before public disclosure with no known in-the-wild exploitation; the Unit 42 case was an observed malicious injection attempt without confirmed successful bypass of a deployed ad-review agent.",
    },
}

LEARNER_EXPECTED = {
    "eyebrow": "ТРИ ПРИМЕРА · ПЯТЬ ПРАВИЛ",
    "heading": "Безопасность ИИ",
    "titles": [
        "Replit: автоматическое действие привело к удалению данных.",
        "Copilot: письмо содержало скрытые инструкции.",
        "Unit 42: на веб-страницах нашли скрытые команды.",
    ],
    "rules": [
        "01 · Проверяйте источники",
        "02 · Берегите личные данные",
        "03 · Отличайте данные от указаний",
        "04 · Согласовывайте важные действия",
        "05 · Проверяйте результат",
    ],
    "distinction": "Примеры различаются: Replit — реальный случай удаления данных; EchoLeak — исправленная уязвимость без подтверждённой эксплуатации в открытых источниках; Unit 42 — обнаруженная попытка скрытого управления ИИ, без подтверждённого успешного обхода.",
}

def req(cond: bool, message: str) -> None:
    global checks
    checks += 1
    if not cond:
        errors.append(message)

# Source wiring.
component = ROOT / "components" / "workshop" / "AgentSafetyLesson.tsx"
req(component.is_file(), "missing AgentSafetyLesson.tsx")
if component.is_file():
    source = component.read_text(encoding="utf-8")
    for marker in [
        'id="agent-safety"',
        'styles.agentSafetyCases',
        'styles.agentSafetyRules',
        'target="_blank"',
        'rel="noopener noreferrer"',
        "Replit Agent удалил данные production-базы.",
        "EchoLeak showed that incoming data can become an instruction.",
        "Unit 42 found hidden prompts on malicious webpages.",
        "01 · Сначала read-only",
        "05 · Verify after the effect",
    ]:
        req(marker in source, f"AgentSafetyLesson source missing {marker!r}")
    for url in SOURCES:
        req(source.count(url) == 2, f"AgentSafetyLesson source URL count drift for {url}")

audience = (ROOT / "components" / "workshop" / "WorkshopAudience.tsx").read_text(encoding="utf-8")
business = (ROOT / "components" / "workshop" / "WorkshopBusiness.tsx").read_text(encoding="utf-8")
req('import { AgentSafetyLesson } from "./AgentSafetyLesson";' in audience, "WorkshopAudience import missing")
if E34:
    req('{audience!=="kids"&&en&&<AgentSafetyLesson locale={locale}/>}' in audience, "EN legacy safety mount missing")
    req('{audience!=="kids"&&!en&&<AgentSafetyLesson locale={locale} mode="learner"/>}' in audience, "RU learner safety mount missing")
else:
    req('{audience!=="kids"&&<AgentSafetyLesson locale={locale}/>}' in audience, "WorkshopAudience N15 conditional missing")
req('import { AgentSafetyLesson } from "./AgentSafetyLesson";' in business, "WorkshopBusiness import missing")
req('<AgentSafetyLesson locale={locale}/>' in business, "WorkshopBusiness N15 mount missing")

source_css = (ROOT / "components" / "workshop" / "WorkshopShell.module.css").read_text(encoding="utf-8")
for marker in [
    "/* N15 · safe AI-agent lesson.",
    ".agentSafetyCases{display:grid",
    ".agentSafetyRules{list-style:none",
    "@media(max-width:620px){.agentSafetyCases,.agentSafetyRules{grid-template-columns:1fr}",
]:
    req(marker in source_css, f"source CSS missing {marker!r}")

# Static surfaces.
for rel, locale in TARGETS.items():
    path = LIVE / rel
    req(path.is_file(), f"{rel}: missing")
    if not path.is_file():
        continue
    raw = path.read_text(encoding="utf-8")
    expected = LEARNER_EXPECTED if E34 and rel in {"personal.html", "teens.html"} else EXPECTED[locale]
    req(raw.count('data-n15-agent-safety="true"') == 1, f"{rel}: N15 block count")
    req(raw.count('class="agentSafetyCase"') == 3, f"{rel}: case count")
    block_match = re.search(
        r'<section class="section agentSafety" id="agent-safety" data-n15-agent-safety="true">([\s\S]*?)</section>',
        raw,
    )
    req(block_match is not None, f"{rel}: N15 section parse")
    if not block_match:
        continue
    block = block_match.group(1)
    req(expected["eyebrow"] in block, f"{rel}: eyebrow drift")
    req(expected["heading"] in block, f"{rel}: heading drift")
    for title in expected["titles"]:
        req(title in block, f"{rel}: missing case title {title!r}")
    for title in expected["rules"]:
        req(title in block, f"{rel}: missing rule {title!r}")
    req(expected["distinction"] in block, f"{rel}: case distinction drift")
    req(block.count("<li><strong>") == 5, f"{rel}: rule count")
    for url in SOURCES:
        req(block.count(f'href="{url}"') == 1, f"{rel}: source link count {url}")
    req(block.count('target="_blank" rel="noopener noreferrer"') == 3, f"{rel}: external link hardening")
    req("<form" not in block.lower(), f"{rel}: N15 must not contain form")
    req("<script" not in block.lower(), f"{rel}: N15 must not contain script")
    if "business" in rel:
        marker='id="pilot-simulator"' if E32 and rel=="business.html" else "IMPLEMENTATION PILOT"
        req(marker in raw and raw.index('data-n15-agent-safety="true"') < raw.index(marker), f"{rel}: block position")
    else:
        if E34 and rel in {"personal.html", "teens.html"}:
            req(raw.index('data-n15-agent-safety="true"') > raw.index('id="pricing"'), f"{rel}: E3.4 block after packages")
            req(block.count("<h2>") == 1, f"{rel}: E3.4 one safety H2")
            req(block.count("<h2>" + expected["heading"] + "</h2>") == 1, f"{rel}: E3.4 exact learner H2")
        else:
            req(raw.index('data-n15-agent-safety="true"') < raw.index('id="pricing"'), f"{rel}: block position")

for rel in ["kids.html", "en/kids.html"]:
    raw = (LIVE / rel).read_text(encoding="utf-8")
    req('data-n15-agent-safety="true"' not in raw, f"{rel}: kids must not receive N15 block")

static_css = (LIVE / "workshop.css").read_text(encoding="utf-8")
for marker in [
    "/* N15_AGENT_SAFETY_START */",
    "/* N15_AGENT_SAFETY_END */",
    ".agentSafetyCases{display:grid",
    ".agentSafetyRules{list-style:none",
]:
    req(marker in static_css, f"static CSS missing {marker!r}")

builder = (ROOT / "scripts" / "build_n15_agent_safety.py").read_text(encoding="utf-8")
for marker in [
    "N15_BUILD_PASS",
    'data-n15-agent-safety="true"',
    "N15_AGENT_SAFETY_START",
    "page_changes={changed}",
]:
    req(marker in builder, f"builder missing {marker!r}")

print(f"N15_AGENT_SAFETY_CHECK checks={checks} pages={len(TARGETS)} cases=3 rules=5 sources=3")
if errors:
    print("N15_AGENT_SAFETY_FAIL")
    for error in errors:
        print("-", error)
    sys.exit(1)
print("N15_AGENT_SAFETY_PASS")
