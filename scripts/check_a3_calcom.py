#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy" / "live"
CALCOM = "https://cal.com/robert-dumanyan-vlck0x/15min"
errors: list[str] = []
checks = 0

STARTS = {
    "start.html": ("ru", "Бесплатный звонок-знакомство · 15 минут"),
    "en/start.html": ("en", "Free 15-minute intro call"),
}
OTHER_RU = ["index.html","kids.html","teens.html","parents.html","personal.html","business.html","pricing.html","matcher.html"]
OTHER_EN = ["en.html","en/kids.html","en/teens.html","en/parents.html","en/personal.html","en/business.html","en/pricing.html","en/matcher.html"]

def req(cond: bool, message: str) -> None:
    global checks
    checks += 1
    if not cond:
        errors.append(message)

# Source authority.
lib = (ROOT / "lib" / "e1_4.ts").read_text(encoding="utf-8")
req(f'calcomUrl: "{CALCOM}"' in lib, "e1_4 calcom URL missing")

cta = (ROOT / "components" / "IntroCallCta.tsx").read_text(encoding="utf-8")
for marker in [
    '"whatsapp" | "telegram" | "calcom"',
    "bookingHref?: string",
    'const primaryHref = bookingHref ?? introWhatsappHref(locale);',
    'const primaryChannel = bookingHref ? "calcom" : "whatsapp";',
    'data-intro-call-channel={primaryChannel}',
    'onClick={() => track(primaryChannel)}',
    'data-intro-call-channel="telegram"',
]:
    req(marker in cta, f"IntroCallCta missing {marker!r}")

start_source = (ROOT / "components" / "workshop" / "WorkshopStart.tsx").read_text(encoding="utf-8")
req('import { introCall } from "@/lib/e1_4";' in start_source, "WorkshopStart introCall import missing")
req('<IntroCallCta locale={locale} bookingHref={introCall.calcomUrl}/>' in start_source, "WorkshopStart Cal.com mount missing")

# Static /start only.
for rel, (locale, label) in STARTS.items():
    text = (LIVE / rel).read_text(encoding="utf-8")
    req(text.count("data-e14-entry") == 1, f"{rel}: e14 entry count")
    m = re.search(r'<div class="e14EntryStart" data-e14-entry>([\s\S]*?)</div></article><article class="e14EntryCard e14DiagnosticCard">', text)
    req(m is not None, f"{rel}: first-step block parse")
    if not m:
        continue
    block = m.group(1)
    req(label in block, f"{rel}: intro label")
    req(block.count(CALCOM) == 1, f"{rel}: Cal.com URL count")
    req(block.count('data-intro-call-channel="calcom"') == 1, f"{rel}: calcom tracker count")
    req(block.count('data-intro-call-channel="telegram"') == 1, f"{rel}: telegram fallback count")
    req('data-intro-call-channel="whatsapp"' not in block, f"{rel}: WhatsApp must not remain primary")
    req('target="_blank" rel="noopener noreferrer"' in block, f"{rel}: external link hardening")
    req("<form" not in block.lower(), f"{rel}: no form in intro block")
    req("<script" not in block.lower(), f"{rel}: no script in intro block")

# Other 16 surfaces remain WhatsApp + Telegram and must not gain Cal.com.
ru_wa = "https://wa.me/66649701204?text=" + quote("Здравствуйте! Хочу записаться на бесплатный звонок-знакомство, 15 минут.", safe="")
en_wa = "https://wa.me/66649701204?text=" + quote("Hi! I'd like to book the free 15-minute intro call.", safe="")
for files, wa in [(OTHER_RU, ru_wa), (OTHER_EN, en_wa)]:
    for rel in files:
        text = (LIVE / rel).read_text(encoding="utf-8")
        req(CALCOM not in text, f"{rel}: Cal.com leaked outside /start")
        req(text.count('data-intro-call-channel="whatsapp"') == 1, f"{rel}: WhatsApp tracker drift")
        req(text.count('data-intro-call-channel="telegram"') == 1, f"{rel}: Telegram tracker drift")
        req(wa in text, f"{rel}: WhatsApp URL drift")

runtime = (LIVE / "lab-command.js").read_text(encoding="utf-8")
req('channel!=="whatsapp"&&channel!=="telegram"&&channel!=="calcom"' in runtime, "static tracker does not admit calcom")
req('name:"intro_call_click"' in runtime, "intro_call_click event missing")

# No route expansion.
public = [p for p in LIVE.rglob("*.html") if p.name != "404.html"]
req(len(public) == 52, f"public route count {len(public)} != 52")

print(f"A3_CALCOM_CHECK checks={checks} start_pages=2 unchanged_intro_surfaces=16 public_routes={len(public)}")
if errors:
    print("A3_CALCOM_FAIL")
    for error in errors:
        print("-", error)
    sys.exit(1)
print("A3_CALCOM_PASS")
