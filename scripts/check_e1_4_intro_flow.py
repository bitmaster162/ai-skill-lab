#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import quote
import sys
ROOT=Path(__file__).resolve().parents[1]; LIVE=ROOT/"deploy/live"
RU_LABEL="Бесплатный звонок-знакомство · 15 минут"; EN_LABEL="Free 15-minute intro call"
RU_DIAG="Диагностика $120 · 60 минут · Зачтём в стоимость пакета при покупке в течение 14 дней."
EN_DIAG="Diagnostic session $120 · 60 minutes · Credited toward a package purchased within 14 days."
RU_WA="https://wa.me/66649701204?text="+quote("Здравствуйте! Хочу записаться на бесплатный звонок-знакомство, 15 минут.",safe="")
EN_WA="https://wa.me/66649701204?text="+quote("Hi! I'd like to book the free 15-minute intro call.",safe="")
RU=["index.html","start.html","kids.html","teens.html","parents.html","personal.html","business.html","pricing.html","matcher.html"]
EN=["en.html","en/start.html","en/kids.html","en/teens.html","en/parents.html","en/personal.html","en/business.html","en/pricing.html","en/matcher.html"]
problems=[]
for files,label,diag,wa in [(RU,RU_LABEL,RU_DIAG,RU_WA),(EN,EN_LABEL,EN_DIAG,EN_WA)]:
    for rel in files:
        text=(LIVE/rel).read_text(encoding="utf-8")
        if text.count("data-e14-entry")!=1: problems.append(f"{rel}: e14 entry count")
        if label not in text: problems.append(f"{rel}: intro label missing")
        if diag not in text: problems.append(f"{rel}: diagnostic summary missing")
        if wa not in text: problems.append(f"{rel}: WhatsApp route missing")
        if 'data-intro-call-channel="telegram"' not in text: problems.append(f"{rel}: Telegram tracker missing")
if "intro_call_click" not in (LIVE/"lab-command.js").read_text(encoding="utf-8"): problems.append("lab-command.js event missing")
css=(LIVE/"workshop.css").read_text(encoding="utf-8")
if ".e14EntryStart" not in css or "@media(max-width:620px)" not in css: problems.append("responsive CSS missing")
if problems:
    print("\n".join("FAIL: "+p for p in problems)); sys.exit(1)
print("E1_4_INTRO_FLOW_PASS routes=18 event=intro_call_click channels=2")
