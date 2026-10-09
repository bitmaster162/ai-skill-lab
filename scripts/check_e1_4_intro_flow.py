#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import quote
import json, sys

ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/"deploy/live"

RU_LABEL="Бесплатный звонок-знакомство · 15 минут"
EN_LABEL="Free 15-minute intro call"
RU_DIAG="Диагностика $120 · 60 минут · Зачтём в стоимость пакета при покупке в течение 14 дней."
EN_DIAG="Diagnostic session $120 · 60 minutes · Credited toward a package purchased within 14 days."
RU_WA="https://wa.me/66649701204?text="+quote("Здравствуйте! Хочу записаться на бесплатный звонок-знакомство, 15 минут.",safe="")
EN_WA="https://wa.me/66649701204?text="+quote("Hi! I'd like to book the free 15-minute intro call.",safe="")
CALCOM="https://cal.com/robert-dumanyan-vlck0x/15min"

RU=["index.html","start.html","kids.html","teens.html","parents.html","personal.html","business.html","pricing.html","matcher.html"]
EN=["en.html","en/start.html","en/kids.html","en/teens.html","en/parents.html","en/personal.html","en/business.html","en/pricing.html","en/matcher.html"]
START={"start.html","en/start.html"}

problems=[]
for files,label,diag,wa in [(RU,RU_LABEL,RU_DIAG,RU_WA),(EN,EN_LABEL,EN_DIAG,EN_WA)]:
    for rel in files:
        text=(LIVE/rel).read_text(encoding="utf-8")
        if text.count("data-e14-entry")!=1:
            problems.append(f"{rel}: e14 entry count")
        if label not in text:
            problems.append(f"{rel}: intro label missing")
        if diag not in text:
            problems.append(f"{rel}: diagnostic summary missing")
        if rel in START:
            if CALCOM not in text:
                problems.append(f"{rel}: Cal.com route missing")
            if 'data-intro-call-channel="calcom"' not in text:
                problems.append(f"{rel}: Cal.com tracker missing")
        else:
            if wa not in text:
                problems.append(f"{rel}: WhatsApp route missing")
            if 'data-intro-call-channel="whatsapp"' not in text:
                problems.append(f"{rel}: WhatsApp tracker missing")
        if 'data-intro-call-channel="telegram"' not in text:
            problems.append(f"{rel}: Telegram tracker missing")

runtime=(LIVE/"lab-command.js").read_text(encoding="utf-8")
release=json.loads((LIVE/"_release.json").read_text(encoding="utf-8")).get("release_id")
if release in {"E3_8_LEAD_EVENTS_R1","E3_1_RU_SEO_R1","E3_3_H1_ACTION_R1","E3_2_RU_GLOSSARY_R1","E3_4_AI_SAFETY_AUDIENCE_R1"}:
    for marker in ['fetch("/api/event"','"cal.com":"cal"','n+"_click"']:
        if marker not in runtime:
            problems.append(f"lab-command.js E3.8 event marker missing {marker}")
else:
    if "intro_call_click" not in runtime:
        problems.append("lab-command.js event missing")
    if 'channel!=="whatsapp"&&channel!=="telegram"&&channel!=="calcom"' not in runtime:
        problems.append("lab-command.js calcom channel missing")

css=(LIVE/"workshop.css").read_text(encoding="utf-8")
if ".e14EntryStart" not in css or "@media(max-width:620px)" not in css:
    problems.append("responsive CSS missing")

if problems:
    print("\n".join("FAIL: "+p for p in problems))
    sys.exit(1)

print(f"E1_4_INTRO_FLOW_PASS routes=18 event={'first_party_e3_8' if release in {'E3_8_LEAD_EVENTS_R1','E3_1_RU_SEO_R1','E3_3_H1_ACTION_R1','E3_2_RU_GLOSSARY_R1','E3_4_AI_SAFETY_AUDIENCE_R1'} else 'intro_call_click'} channels=3 start_calcom=2")
