#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy" / "live"
PUBLIC = ROOT / "public"
ASSET = "robert-dumanyan-mentor.webp"
ASSET_SHA256 = "1ccb8e47747706274a47302ed1a379748269de24890b5778ab721fd62ff8251b"
SOURCE_PROFILE_URL = "https://cal.com/robert-dumanyan-vlck0x"
SOURCE_AVATAR_JPEG_SHA256 = "6fbefde3096a05011dcbc911a5539253500389c9a63a330acf4503b039722418"
GITHUB = "https://github.com/bitmaster162"
LINKEDIN = "https://www.linkedin.com/in/robert-dumanyan-984171335/"

PROFILE = {
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

CSS = r"""
/* A5_MENTOR_START */
.mentorSection{padding:clamp(48px,7vw,88px) clamp(18px,6vw,92px);background:var(--panel)}
.mentorCard{width:min(1180px,100%);margin:auto;display:grid;grid-template-columns:192px minmax(0,1fr);gap:clamp(24px,4vw,52px);align-items:center;padding:clamp(22px,3vw,34px);border:1px solid var(--border);border-radius:24px;background:var(--card)}
.mentorPhoto{width:192px;max-width:100%}
.mentorPhoto img{display:block;width:100%;height:auto;aspect-ratio:1/1;object-fit:cover;border:1px solid var(--border);border-radius:20px}
.mentorCopy{min-width:0}
.mentorEyebrow{display:block;margin-bottom:10px;color:var(--muted);font-weight:850;letter-spacing:.06em}
.mentorCopy h2{margin:0 0 8px}
.mentorCopy>strong{display:block;margin-bottom:14px}
.mentorCopy>p{max-width:820px;margin:0;color:var(--second);line-height:1.7}
.mentorFocus{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0}
.mentorFocus span{padding:8px 10px;border:1px solid var(--border);border-radius:999px;background:var(--ground);overflow-wrap:anywhere}
.mentorLinks{display:flex;flex-wrap:wrap;gap:10px}
.mentorLinks a{min-height:48px;padding:0 18px;display:inline-flex;align-items:center;border:1px solid var(--strong);border-radius:999px;color:var(--ink);font-weight:700}
.mentorLinks a:hover,.mentorLinks a:focus-visible{background:var(--raised)}
@media(max-width:620px){.mentorCard{grid-template-columns:1fr}.mentorPhoto{width:144px}.mentorLinks{display:grid;grid-template-columns:1fr}.mentorLinks a{justify-content:center}}
/* A5_MENTOR_END */
""".strip()

TARGETS = {
    "index.html": ("ru", '<section class="workshopSection"><div class="sectionHead"><span>ВЫБЕРИТЕ ТРЕК</span>'),
    "en.html": ("en", '<section class="workshopSection"><div class="sectionHead"><span>CHOOSE A TRACK</span>'),
    "about.html": ("ru", '<section class="section dark">'),
    "en/about.html": ("en", '<section class="section dark">'),
}

def esc(value: str) -> str:
    return html.escape(value, quote=True)

def mentor_block(locale: str) -> str:
    p = PROFILE[locale]
    chips = "".join(f"<span>{esc(item)}</span>" for item in FOCUS)
    return (
        '<section class="mentorSection" data-a5-mentor="true">'
        '<div class="mentorCard">'
        '<div class="mentorPhoto">'
        f'<img src="/{ASSET}" alt="{esc(p["alt"])}" width="192" height="192" loading="lazy" decoding="async">'
        '</div>'
        '<div class="mentorCopy">'
        f'<span class="mentorEyebrow">{esc(p["eyebrow"])}</span>'
        f'<h2>{esc(p["name"])}</h2>'
        f'<strong>{esc(p["role"])}</strong>'
        f'<p>{esc(p["summary"])}</p>'
        f'<div class="mentorFocus" aria-label="{"Areas of practice" if locale == "en" else "Направления практики"}">{chips}</div>'
        '<div class="mentorLinks">'
        f'<a href="{GITHUB}" target="_blank" rel="noopener noreferrer">GitHub ↗</a>'
        f'<a href="{LINKEDIN}" target="_blank" rel="noopener noreferrer">LinkedIn ↗</a>'
        '</div></div></div></section>'
    )

def update_page(path: Path, locale: str, anchor: str) -> bool:
    raw = path.read_text(encoding="utf-8")
    block = mentor_block(locale)
    pattern = re.compile(r'<section class="mentorSection" data-a5-mentor="true">[\s\S]*?</section>')
    if pattern.search(raw):
        new, count = pattern.subn(block, raw, count=1)
        if count != 1:
            raise RuntimeError(f"{path}: existing A5 block count={count}")
    else:
        if raw.count(anchor) != 1:
            raise RuntimeError(f"{path}: insertion anchor count={raw.count(anchor)}")
        new = raw.replace(anchor, block + anchor, 1)
    if new != raw:
        path.write_text(new, encoding="utf-8", newline="\n")
        return True
    return False

def update_person_jsonld(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8")
    pattern = re.compile(r'(<script type="application/ld\+json">)([\s\S]*?)(</script>)')
    found = 0
    changed = False
    pieces = []
    pos = 0
    for match in pattern.finditer(raw):
        pieces.append(raw[pos:match.start()])
        body = match.group(2)
        replacement = match.group(0)
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = None
        if isinstance(data, dict) and data.get("@type") == "Person" and data.get("@id") == "https://aiskillab.work/about#person":
            found += 1
            data["name"] = "Robert Dumanyan"
            data["jobTitle"] = "Founder / instructor"
            data["image"] = f"https://aiskillab.work/{ASSET}"
            data["sameAs"] = ["https://t.me/BiTFormer", GITHUB, LINKEDIN]
            compact = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
            replacement = match.group(1) + compact + match.group(3)
            changed = changed or replacement != match.group(0)
        pieces.append(replacement)
        pos = match.end()
    pieces.append(raw[pos:])
    if found != 1:
        raise RuntimeError(f"{path}: Person JSON-LD count={found}")
    new = "".join(pieces)
    if new != raw:
        path.write_text(new, encoding="utf-8", newline="\n")
        return True
    return False

def update_css() -> bool:
    path = LIVE / "workshop.css"
    raw = path.read_text(encoding="utf-8")
    pattern = re.compile(r"/\* A5_MENTOR_START \*/[\s\S]*?/\* A5_MENTOR_END \*/")
    new = pattern.sub(CSS, raw) if pattern.search(raw) else raw.rstrip() + "\n" + CSS + "\n"
    if new != raw:
        path.write_text(new, encoding="utf-8", newline="\n")
        return True
    return False

def copy_asset() -> bool:
    src = PUBLIC / ASSET
    dst = LIVE / ASSET
    data = src.read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    if actual != ASSET_SHA256:
        raise RuntimeError(f"source asset SHA drift: {actual}")
    if dst.exists() and dst.read_bytes() == data:
        return False
    shutil.copyfile(src, dst)
    return True

def main() -> int:
    asset_changed = copy_asset()
    page_changes = 0
    for rel, (locale, anchor) in TARGETS.items():
        page_changes += int(update_page(LIVE / rel, locale, anchor))
    jsonld_changes = sum(int(update_person_jsonld(LIVE / rel)) for rel in ("about.html", "en/about.html"))
    css_changed = update_css()
    print(
        f"A5_MENTOR_BUILD_PASS pages=4 page_changes={page_changes} "
        f"jsonld_changes={jsonld_changes} asset_changed={str(asset_changed).lower()} "
        f"css_changed={str(css_changed).lower()} asset_sha256={ASSET_SHA256}"
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
