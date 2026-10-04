#!/usr/bin/env python3
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy" / "live"

AREAS = {
    "ru": [
        ("Rawai / Nai Harn", "Юг Phuket. Локальная встреча — только после подтверждения места и времени."),
        ("Chalong", "Южно-центральная часть острова. Подходит как ориентир для согласования очной сессии."),
        ("Kata / Karon", "Западное побережье. Доступность конкретного места подтверждаем до бронирования."),
        ("Phuket Town", "Центральная городская зона. Точка встречи определяется отдельно под конкретную сессию."),
    ],
    "en": [
        ("Rawai / Nai Harn", "South Phuket. An in-person session is confirmed only after venue and timing are agreed."),
        ("Chalong", "South-central Phuket. Used as a local coordination area for an agreed in-person session."),
        ("Kata / Karon", "West coast. Availability of a specific venue is confirmed before booking."),
        ("Phuket Town", "Central urban area. The meeting point is agreed separately for each session."),
    ],
}

FORMATS = {
    "ru": [
        ("LOCAL 1:1", "Очная персональная сессия", "Место и время согласуем заранее. AI Skill Lab не заявляет постоянный учебный центр или публичный classroom address."),
        ("ONLINE 1:1", "Персональная работа online", "Экран, совместная сборка проектов и персональный маршрут работают независимо от страны."),
        ("HYBRID", "Часть очно, часть online", "Если программе нужен смешанный режим, очные и online-сессии можно сочетать после согласования маршрута."),
    ],
    "en": [
        ("LOCAL 1:1", "In-person one-to-one", "Venue and timing are agreed in advance. AI Skill Lab does not claim a permanent school location or public classroom address."),
        ("ONLINE 1:1", "One-to-one online", "Screen sharing, project building and a personal route work regardless of country."),
        ("HYBRID", "Local plus online", "If a program benefits from both, in-person and online sessions can be combined after the route is agreed."),
    ],
}

CSS = r"""
/* A4_PHUKET_LOCAL_START */
.phuketLocal,.phuketFormats{padding:clamp(48px,7vw,88px) clamp(18px,6vw,92px)}
.phuketLocal{background:var(--ground)}
.phuketFormats{background:var(--panel)}
.phuketLocalHead{max-width:860px;margin:0 0 30px}
.phuketLocalHead>span{display:block;color:var(--muted);font-weight:850;letter-spacing:.06em;margin-bottom:12px}
.phuketLocalHead h2{margin:0 0 14px}
.phuketLocalHead p{margin:0;color:var(--second);line-height:1.7}
.phuketAreaGrid,.phuketFormatGrid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.phuketAreaGrid article,.phuketFormatGrid article{min-width:0;padding:22px;border:1px solid var(--border);border-radius:20px;background:var(--card)}
.phuketAreaGrid strong,.phuketFormatGrid>article>span{display:block;margin-bottom:12px;font-weight:850}
.phuketAreaGrid p,.phuketFormatGrid p{margin:0;color:var(--second);line-height:1.65}
.phuketFormatGrid{grid-template-columns:repeat(3,minmax(0,1fr))}
.phuketFormatTitle{display:block;margin:10px 0 12px}
.phuketLocalNote{max-width:860px;margin:24px 0 0;color:var(--muted);line-height:1.7}
@media(max-width:980px){.phuketAreaGrid{grid-template-columns:1fr 1fr}.phuketFormatGrid{grid-template-columns:1fr}}
@media(max-width:620px){.phuketLocal,.phuketFormats{padding:44px 18px}.phuketAreaGrid{grid-template-columns:1fr}.phuketAreaGrid article,.phuketFormatGrid article{padding:20px}}
/* A4_PHUKET_LOCAL_END */
""".strip()

TARGETS = {
    "phuket.html": "ru",
    "en/phuket.html": "en",
}

def esc(value: str) -> str:
    return html.escape(value, quote=True)

def block(locale: str) -> str:
    en = locale == "en"
    areas = "".join(
        f'<article><strong>{esc(name)}</strong><p>{esc(note)}</p></article>'
        for name, note in AREAS[locale]
    )
    formats = "".join(
        f'<article><span>{esc(tag)}</span><strong class="phuketFormatTitle">{esc(title)}</strong><p>{esc(body)}</p></article>'
        for tag, title, body in FORMATS[locale]
    )
    eyebrow = "PHUKET · LOCAL COORDINATION" if en else "PHUKET · ЛОКАЛЬНАЯ КООРДИНАЦИЯ"
    h2 = "Real areas, no invented campus." if en else "Реальные районы, без выдуманного кампуса."
    lead = (
        "For local planning we use recognizable Phuket areas. They are coordination areas, not branches or permanent classrooms. The exact venue, availability and travel time are confirmed before booking."
        if en else
        "Для локального планирования используем понятные районы Phuket. Это зоны координации, а не филиалы и не постоянные классы. Точное место, доступность и время в пути подтверждаем до бронирования."
    )
    format_h2 = "Choose geography after the learning route." if en else "Сначала маршрут обучения, потом география."
    youth = (
        "For minors, contact, scheduling and service approval remain with a parent or legal guardian."
        if en else
        "Для несовершеннолетних контакт, расписание и согласование сервисов остаются за родителем или законным представителем."
    )
    return (
        '<section class="phuketLocal" data-a4-phuket-local="true">'
        f'<div class="phuketLocalHead"><span>{esc(eyebrow)}</span><h2>{esc(h2)}</h2><p>{esc(lead)}</p></div>'
        f'<div class="phuketAreaGrid">{areas}</div>'
        '</section>'
        '<section class="phuketFormats" data-a4-phuket-formats="true">'
        f'<div class="phuketLocalHead"><span>{"FORMAT" if en else "ФОРМАТ"}</span><h2>{esc(format_h2)}</h2></div>'
        f'<div class="phuketFormatGrid">{formats}</div>'
        f'<p class="phuketLocalNote">{esc(youth)}</p>'
        '</section>'
    )

def update_page(path: Path, locale: str) -> bool:
    raw = path.read_text(encoding="utf-8")
    if 'data-a4-phuket-local="true"' in raw:
        pattern = re.compile(
            r'<section class="phuketLocal" data-a4-phuket-local="true">[\s\S]*?'
            r'</section><section class="phuketFormats" data-a4-phuket-formats="true">[\s\S]*?</section>'
        )
        new, count = pattern.subn(block(locale), raw, count=1)
        if count != 1:
            raise RuntimeError(f"{path}: existing A4 block replacement failed")
    else:
        if raw.count("</main>") != 1:
            raise RuntimeError(f"{path}: expected one </main>, got {raw.count('</main>')}")
        new = raw.replace("</main>", block(locale) + "</main>", 1)
    if new != raw:
        path.write_text(new, encoding="utf-8", newline="\n")
        return True
    return False

def update_css() -> bool:
    path = LIVE / "workshop.css"
    raw = path.read_text(encoding="utf-8")
    pattern = re.compile(r"/\* A4_PHUKET_LOCAL_START \*/[\s\S]*?/\* A4_PHUKET_LOCAL_END \*/")
    new = pattern.sub(CSS, raw) if pattern.search(raw) else raw.rstrip() + "\n" + CSS + "\n"
    if new != raw:
        path.write_text(new, encoding="utf-8", newline="\n")
        return True
    return False

def main() -> int:
    page_changes = 0
    for rel, locale in TARGETS.items():
        page_changes += int(update_page(LIVE / rel, locale))
    css_changed = update_css()
    print(f"A4_PHUKET_BUILD_PASS pages=2 page_changes={page_changes} css_changed={str(css_changed).lower()} areas=6 area_cards=4 formats=3")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
