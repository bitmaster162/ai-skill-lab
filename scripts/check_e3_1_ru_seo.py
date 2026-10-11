#!/usr/bin/env python3
"""E3.1: exact approved RU SEO copy and limited sitewide lexical parity."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import json
import hashlib

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy" / "live"
RELEASE_ID = json.loads((LIVE / "_release.json").read_text(encoding="utf-8")).get("release_id")
EXACT = {
    "/": (
        "Обучение ИИ 1-на-1 на Пхукете и онлайн — AI Skill Lab",
        "Персональные занятия по ИИ и нейросетям для взрослых, подростков, детей и команд. Пхукет и онлайн, на русском и английском. Бесплатный звонок 15 минут.",
    ),
    "/kids": (
        "ИИ для детей 8–13 лет на Пхукете и онлайн — AI Skill Lab",
        "Занятия по ИИ и нейросетям для детей 8–13 лет: свой творческий проект вместе со взрослым, правила приватности и безопасная практика. Пхукет и онлайн.",
    ),
    "/teens": (
        "ИИ для подростков 14–18 на Пхукете и онлайн — AI Skill Lab",
        "Подростки 14–18 лет работают с ИИ и нейросетями: исследования, код, портфолио и свои проекты с проверкой результата. Пхукет и онлайн.",
    ),
    "/personal": (
        "Персональное обучение ИИ 1-на-1 — AI Skill Lab · Пхукет",
        "Занятия по ИИ и нейросетям 1-на-1 вокруг вашей реальной задачи: практика, свой проект и разбор инструментов. На Пхукете или онлайн.",
    ),
    "/business": (
        "ИИ для бизнеса на Пхукете: обучение команды — AI Skill Lab",
        "Обучение команды работе с ИИ, разбор процессов и один пилот — от выбора задачи до проверяемого результата, без лишних обещаний. Пхукет и онлайн.",
    ),
    "/pricing": (
        "Цены на обучение ИИ: сессии, пакеты, пилоты — AI Skill Lab",
        "Цены AI Skill Lab в долларах: бесплатный звонок 15 минут, диагностика $120, пакеты занятий по 60 минут, обучение команд и пилоты для бизнеса.",
    ),
    "/phuket": (
        "Обучение ИИ на Пхукете очно и онлайн — AI Skill Lab",
        "Очные занятия по ИИ на Пхукете по договорённости и онлайн для тех, кто в других странах. Несовершеннолетние занимаются через взрослого.",
    ),
    "/start": (
        "Записаться на обучение ИИ — AI Skill Lab",
        "Оставьте короткую заявку или напишите в Telegram, WhatsApp, LINE или на почту. Бесплатный звонок 15 минут, ответ в течение 1–2 рабочих дней.",
    ),
}
TERM = re.compile(r"ИИ|нейросет", re.IGNORECASE)


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.description = ""
        self.og_title = ""
        self.og_description = ""
        self.twitter_title = ""
        self.lang = ""
        self.in_title = False
        self.in_body = False
        self.in_h1 = False
        self.after_h1 = False
        self.in_first_p = False
        self.first_p_done = False
        self.skip = 0
        self.first_p: list[str] = []
        self.h1: list[str] = []
        self.body: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang") or ""
        if tag == "body":
            self.in_body = True
        if tag in ("script", "style"):
            self.skip += 1
        if tag == "title":
            self.in_title = True
        if tag == "meta":
            key = a.get("name") or a.get("property")
            val = a.get("content") or ""
            if key == "description":
                self.description = val
            elif key == "og:title":
                self.og_title = val
            elif key == "og:description":
                self.og_description = val
            elif key == "twitter:title":
                self.twitter_title = val
        if tag == "h1":
            self.in_h1 = True
        if tag == "p" and self.after_h1 and not self.first_p_done and not self.in_first_p:
            self.in_first_p = True

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        if tag == "title":
            self.in_title = False
        if tag == "h1":
            self.in_h1 = False
            self.after_h1 = True
        if tag == "p" and self.in_first_p:
            self.in_first_p = False
            self.first_p_done = True
        if tag == "body":
            self.in_body = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title += data
        if self.skip:
            return
        if self.in_body:
            self.body.append(data)
        if self.in_h1:
            self.h1.append(data)
        if self.in_first_p:
            self.first_p.append(data)


def route_for(path: Path) -> str:
    rel = path.relative_to(LIVE).as_posix()
    if rel == "index.html":
        return "/"
    return "/" + rel.removesuffix(".html")


def main() -> int:
    errors: list[str] = []
    routes = []
    for path in sorted(LIVE.rglob("*.html")):
        route = route_for(path)
        if route.startswith("/en") or route == "/404":
            continue
        page = Page()
        page.feed(path.read_text(encoding="utf-8"))
        title = " ".join(page.title.split())
        desc = page.description.strip()
        lead = " ".join("".join(page.first_p).split())
        h1 = " ".join("".join(page.h1).split())
        visible = " ".join("".join(page.body).split()).replace("Phuket Town", "")
        if page.lang != "ru":
            errors.append(f"{route}: wrong lang={page.lang!r}")
        allow_reviewed_future_title = (
            RELEASE_ID == "T1_6F2_ADULT_FIRST_TASKS_R1"
            and route == "/guides/ai-first-tasks-for-adults"
            and title == "С чего начать работать с AI взрослому: первые задачи"
            and hashlib.sha256((ROOT / "guides/aiskillab/ai-first-tasks-for-adults.ru.md").read_bytes()).hexdigest()
                == "5c5f8d8da100a8657aeefbe5d9044462095e92db341e240a37bdebae57bba61b"
        )
        if not (title and len(title) <= 60 and (TERM.search(title) or allow_reviewed_future_title)):
            errors.append(f"{route}: title missing ИИ/нейросети or length>60: {title!r}")
        if not (lead and TERM.search(lead)):
            errors.append(f"{route}: first paragraph missing ИИ/нейросети: {lead!r}")
        if not (desc and len(desc) <= 160):
            errors.append(f"{route}: description missing or length>160")
        if page.og_title != title or page.twitter_title != title:
            errors.append(f"{route}: OG/twitter title mismatch")
        if page.og_description != desc:
            errors.append(f"{route}: OG description mismatch")
        if "Phuket" in visible:
            errors.append(f"{route}: visible Latin Phuket beyond permitted district name")
        if route in EXACT and (title, desc) != EXACT[route]:
            errors.append(f"{route}: exact approved title/description mismatch")
        if route == "/" and lead.count("искусственный интеллект (ИИ) и нейросети") != 1:
            errors.append("/: homepage first paragraph does not contain exact phrase once")
        combined = " ".join([title, desc, h1, lead, visible])
        routes.append(route)
        print(
            f"E3_1_RU_ROUTE path={route} title_len={len(title)} desc_len={len(desc)} "
            f"Пхукет={combined.count('Пхукет')} ИИ={combined.count('ИИ')} "
            f"нейросет={combined.lower().count('нейросет')}"
        )
    expected_routes = 27 if RELEASE_ID == "T1_6F2_ADULT_FIRST_TASKS_R1" else 26
    if len(routes) != expected_routes:
        errors.append(f"expected {expected_routes} RU pages, got {len(routes)}")
    if errors:
        print("E3_1_RU_SEO_FAIL")
        for err in errors:
            print(" - " + err)
        return 1
    print(f"E3_1_RU_SEO_PASS ru_pages={len(routes)} exact_pages={len(EXACT)}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
