#!/usr/bin/env python3
"""Build the local-only U1 RU/EN static markup and external CSS from Claude v2.

Source is byte-pinned, stored in design/ for reproducibility. This script never
touches deploy/live, Git remotes, application APIs, or production resources.
"""
from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "design" / "PHUKET-UNIVERSE-MAKET-v2.html"
EXPECTED_SHA256 = "2d5112f138e7364a83b15471179b5767891e3448e188f0f566d139702dd97024"
OUTPUT_MARKUP = ROOT / "components" / "phuketUniverseMarkup.ts"
OUTPUT_CSS = ROOT / "app" / "phuket-universe.css"

RU_TO_EN = {
    "Орбита": "Orbit",
    "Жильё": "Homes",
    "Агентствам": "For agencies",
    "RU / EN": "Русский",
    "Пхукет · свои люди · жильё": "Phuket · local people · homes",
    "Вселенная Пхукета": "Phuket Universe",
    "Проекты людей, которых мы знаем лично, и жильё в аренду и на продажу — на одной карте острова. Каждая ссылка ведёт прямо к владельцу.": "Projects by people we know personally, plus homes for rent and sale — on one island map. Each link goes directly to its owner.",
    "Найти жильё": "Find a home",
    "Смотреть орбиту": "Explore the orbit",
    "на связи — открывается сайт": "online — opens the project website",
    "скоро": "coming soon",
    "Карта Phuket Universe: остров Пхукет в центре, шесть проектов друзей на орбитах": "Phuket Universe map: Phuket island at the center, with six friends' projects on three orbits",
    "ПХУКЕТ": "PHUKET",
    "01 · ЭКСКУРСИИ": "01 · TOURS",
    "Яков": "Yakov",
    "02 · ГИД": "02 · GUIDE",
    "Стас": "Stas",
    "03 · MUAY THAI": "03 · MUAY THAI",
    "Иван": "Ivan",
    "04 · ДОМ И СЕМЬЯ": "04 · HOME & FAMILY",
    "05 · КОНТЕНТ": "05 · CONTENT",
    "Ростиксон": "Rostikson",
    "06 · РЕСТОРАН · СКОРО": "06 · RESTAURANT · SOON",
    "Нажмите на планету — откроется сайт проекта. Точки на острове — районы для поиска жилья.": "Select a planet to open that project's website. Dots on the island mark areas for the housing search.",
    "01 · Орбита": "01 · Orbit",
    "Проекты друзей": "Friends' projects",
    "Люди, с которыми мы работаем на Пхукете. За свои услуги отвечают они сами — мы даём ссылку и знакомим.": "People we work with in Phuket. They provide their own services; we introduce them and link directly to their sites.",
    "Добавить свой проект": "Suggest your project",
    "01 · Экскурсии": "01 · Tours",
    "на связи": "online",
    "Яков — Phuket Travel": "Yakov — Phuket Travel",
    "Каталог экскурсий и активностей Пхукета. Запросы — через WhatsApp.": "A catalogue of tours and activities in Phuket. Enquiries go through WhatsApp.",
    "Открыть ↗": "Visit ↗",
    "02 · Гид": "02 · Guide",
    "Стас — персональный гид": "Stas — personal guide",
    "Экскурсии, сопровождение и организация дня на Пхукете, островах и в соседних провинциях.": "Tours, personal guiding and day planning in Phuket, nearby islands and neighbouring provinces.",
    "03 · Тренировки": "03 · Training",
    "Иван — Muay Thai и ОФП": "Ivan — Muay Thai & conditioning",
    "Частные тренировки на Пхукете: Muay Thai и Strength &amp; Conditioning, на русском и английском.": "Private Muay Thai and strength &amp; conditioning sessions in Phuket, in Russian and English.",
    "04 · Дом и семья": "04 · Home & family",
    "Помощь дому на Пхукете: готовка, заготовка еды, закупки и немедицинская помощь семье.": "Home and family help in Phuket: cooking, meal prep, shopping and non-medical family assistance.",
    "05 · Контент": "05 · Content",
    "Контент для брендов и ресторанов.": "Content for brands and restaurants.",
    "06 · Ресторан": "06 · Restaurant",
    "Ресторан в Раваи. Сайт готовится к публикации.": "A restaurant in Rawai. Its website is in preparation.",
    "сайт скоро": "website coming soon",
    "Скоро": "Coming soon",
    "02 · Жильё": "02 · Homes",
    "Аренда и продажа — на карте острова": "Rentals and sales across the island",
    "Объекты агентств-партнёров. У нас — район, тип, цена и дата. Фото, описание и контакт — на сайте агентства.": "Listings from partner agencies. We show area, property type, price and date. Photos, details and contacts remain on the agency's own site.",
    "Аренда": "Rent",
    "Продажа": "Sale",
    "Банг Тао": "Bang Tao",
    "Патонг": "Patong",
    "Карон": "Karon",
    "Ката": "Kata",
    "Раваи": "Rawai",
    "Чалонг": "Chalong",
    "Пхукет-таун": "Phuket Town",
    "Весь остров": "All areas",
    "Тип": "Type",
    "Любой": "Any",
    "Квартира или кондо": "Apartment or condo",
    "Вилла": "Villa",
    "Дом": "House",
    "Спальни": "Bedrooms",
    "Любые": "Any",
    "Студия": "Studio",
    "4 и больше": "4 or more",
    "Цена до, ฿": "Maximum price, ฿",
    "Показать": "Show homes",
    "Скоро: агентства добавляют объекты": "Coming soon: agencies are adding homes",
    "Карточки появятся после проверки ссылок у партнёров. Вы агентство? Добавьте свои объекты первыми.": "Listings will appear after partner links have been checked. Are you an agency? Add your homes first.",
    "Агентствам →": "For agencies →",
    "Пример карточки": "Example card",
    "[Район]": "[Area]",
    "[Тип объекта, спальни]": "[Property type, bedrooms]",
    "[Цена] ฿ / мес": "[Price] ฿ / month",
    "[Агентство-партнёр] · обновлено [дата]": "[Partner agency] · updated [date]",
    "На сайт агентства ↗": "Agency website ↗",
    "Показываем только объекты агентств, которые дали согласие, и только с прямой ссылкой на их сайт. Фото и описания остаются у агентства. Цену и наличие проверяйте по ссылке.": "Only properties with agency permission and a direct link to the source can appear here. Photos and descriptions stay with the agency. Check availability and prices at the source.",
    "03 · Агентствам": "03 · For agencies",
    "Ваши объекты — на карте Phuket Universe": "Put your listings on the Phuket Universe map",
    "Карточка ведёт на ваш сайт: заявку получаете вы, а не мы. Фото и тексты не копируем.": "Each card links to your own website. You receive the enquiry directly. We do not copy photos or descriptions.",
    "Условия размещения: [УСЛОВИЯ ДЛЯ АГЕНТСТВ]": "Listing terms: [TERMS FOR AGENCIES]",
    "Написать: robert@aiskillab.work": "Email: robert@aiskillab.work",
    "Пришлите ссылку": "Send your link",
    "На страницу с объявлениями или таблицу: район, тип, спальни, цена.": "Share a listings page or sheet with area, type, bedrooms and price.",
    "Мы проверяем": "We review",
    "Что ссылка ваша и объект актуален. Без проверки карточка не появится.": "We check that the link belongs to you and the listing is current. Unverified listings are not published.",
    "Карточка на карте": "Listing on the map",
    "Район, тип и цена — у нас. Всё остальное и контакт — у вас на сайте.": "We show area, type and price. All details and contact stay on your own website.",
    "Проект AI Skill Lab · Пхукет и онлайн": "An AI Skill Lab project · Phuket and online",
    "Кнопка для подвала сайта": "Site footer link",
    "Ссылки ведут на сайты владельцев. Актуальность объявлений проверяйте у источника.": "Links take you to the owners' websites. Please confirm listing availability with the source.",
}
ATTR_TO_EN = {
    "Phuket Universe — наверх": "Phuket Universe — back to top",
    "Разделы": "Sections",
    "Яков — экскурсии: открыть сайт": "Yakov — tours: open website",
    "Стас — персональный гид: открыть сайт": "Stas — personal guide: open website",
    "Иван — Muay Thai и ОФП: открыть сайт": "Ivan — Muay Thai and conditioning: open website",
    "HAVEN — помощь дому: открыть сайт": "HAVEN — home help: open website",
    "Ростиксон — контент: открыть сайт": "Rostikson — content: open website",
    "Тип сделки": "Deal type",
    "Карта районов Пхукета": "Phuket area map",
    "Район": "Area",
    "Фильтр объектов": "Property filters",
    "например, 40 000": "e.g. 40,000",
    "Пример карточки объекта": "Example listing card",
}

def require(test: bool, explanation: str) -> None:
    if not test:
        raise RuntimeError(explanation)

def source_body() -> str:
    raw = SOURCE.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256, "source v2 SHA-256 drift")
    text = raw.decode("utf-8")
    require(text.count("<body>") == 1 and text.count("</body>") == 1, "source body boundaries")
    body = text.split("<body>", 1)[1].split("</body>", 1)[0]
    body = re.sub(r"<!--[\s\S]*?-->", "", body)
    require(body.count("<section ") == 4 and body.count("<footer ") == 1, "source section boundaries")
    require(body.count('<a href="https://') == 11, "source external links: 5 map + 5 cards + AI Skill Lab")
    return body.strip()

def normalize_markup(body: str, *, locale: str) -> str:
    # Preserve every SVG path/orbit and the exact DOM section order.
    body = body.replace('<section id="top"', '<main id="main"><section id="top"', 1)
    body = body.replace('<footer style=', '</main><footer style=', 1)
    # The sixth planet (Pharaohs Rawai) must not imply a published website.
    begin = body.index(">Pharaohs Rawai</h3>")
    block_end = body.index("</article>", begin)
    block = body[begin:block_end]
    require(block.count('<a href="#orbit"') == 1, "Pharaohs placeholder link drift")
    block = block.replace('<a href="#orbit"', "<div", 1).replace("</a>", "</div>", 1)
    body = body[:begin] + block + body[block_end:]
    # The housing catalogue belongs to U2: do not expose inert active controls
    # or allow a native GET form to leak entered price in the URL.
    require(body.count('<form aria-label="Фильтр объектов"') == 1, "filter boundary")
    body = body.replace('<form aria-label="Фильтр объектов"', '<div role="group" aria-label="Фильтр объектов"', 1)
    require(body.count("</form>") == 1, "housing filter end boundary")
    body = body.replace("</form>", "</div>", 1)
    body = re.sub(r'<button type="button"', '<button type="button" disabled aria-disabled="true"', body)
    body = body.replace('<select id="pu-type"', '<select disabled id="pu-type"', 1)
    body = body.replace('<select id="pu-beds"', '<select disabled id="pu-beds"', 1)
    body = body.replace('<input id="pu-price"', '<input disabled id="pu-price"', 1)
    # Explicit counterpart route, not the source design's #top placeholder.
    locale_route = "/en/phuket-universe" if locale == "ru" else "/phuket-universe"
    require(body.count('href="#top" style="margin-left: 8px;') == 1, "language switch boundary")
    body = body.replace('href="#top" style="margin-left: 8px;', f'href="{locale_route}" style="margin-left: 8px;', 1)
    body = body.replace(">RU / EN<", ">EN →<" if locale == "ru" else ">RU →<", 1)
    # External project and site URLs: only the five approved project links.
    body = re.sub(r'<a href="(https://[^"]+)"', r'<a rel="noopener" href="\1"', body)
    if locale == "en":
        def tr_text(match: re.Match[str]) -> str:
            value = match.group(1)
            t = value.strip()
            if not t:
                return match.group(0)
            if t in RU_TO_EN:
                return ">" + value[:len(value)-len(value.lstrip())] + RU_TO_EN[t] + value[len(value.rstrip()):] + "<"
            return match.group(0)
        body = re.sub(r">([^<>]*)<", tr_text, body)
        for ru, en in ATTR_TO_EN.items():
            for att in ("aria-label", "placeholder", "title"):
                body = body.replace(att + '="' + ru + '"', att + '="' + html.escape(en, quote=True) + '"')
        # The mockup's email subject is Russian; translate only in English route.
        body = body.replace("Phuket%20Universe%20%E2%80%94%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82", "Phuket%20Universe%20%E2%80%94%20project")
        body = body.replace("Phuket%20Universe%20%E2%80%94%20%D0%BE%D0%B1%D1%8A%D0%B5%D0%BA%D1%82%D1%8B", "Phuket%20Universe%20%E2%80%94%20listings")
        require(not re.search(r"[А-Яа-яЁё]", body), "untranslated Cyrillic visible in EN route")
    return body

def externalize_styles(ru: str, en: str) -> tuple[str, str, str]:
    selectors: dict[str, str] = {}
    def convert(raw: str) -> str:
        def on_tag(m: re.Match[str]) -> str:
            tag = m.group(0)
            style = re.search(r'\sstyle="([^"]*)"', tag)
            if not style:
                return tag
            declarations = style.group(1).strip()
            require(declarations != "" and "<" not in declarations, "invalid inline style")
            if declarations not in selectors:
                selectors[declarations] = "pu-s" + f"{len(selectors)+1:03d}"
            cls = selectors[declarations]
            tag = tag[:style.start()] + tag[style.end():]
            if re.search(r'\bclass="', tag):
                tag = tag.replace('class="', 'class="' + cls + " ", 1)
            else:
                tag = re.sub(r'^<([a-zA-Z][a-zA-Z0-9]*)', r'<\1 class="' + cls + '"', tag, count=1)
            return tag
        return re.sub(r'<[A-Za-z][^>]*>', on_tag, raw)
    ru_out, en_out = convert(ru), convert(en)
    require(' style="' not in ru_out and ' style="' not in en_out, "inline style survived")
    require("<script" not in ru_out.lower() and "<script" not in en_out.lower(), "script in static markup")
    css = '''/* U1 faithful styles externalized from locally pinned Claude v2 HTML. */
@font-face{font-family:"Manrope";font-style:normal;font-weight:400 800;font-display:swap;src:url("/fonts/Manrope-cyrillic.woff2") format("woff2");unicode-range:U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116}
@font-face{font-family:"Manrope";font-style:normal;font-weight:400 800;font-display:swap;src:url("/fonts/Manrope-latin.woff2") format("woff2");unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}
.pu-page{background:#070A12;color:#EEF2F6;width:100%;font-family:"Manrope",system-ui,sans-serif;color-scheme:dark}
.pu-page *, .pu-page *::before, .pu-page *::after{box-sizing:border-box}
.pu-page a{color:#EEF2F6}
.pu-page a:hover{color:#FFFFFF}
.pu-page :is(a,button,select,input):focus-visible{outline:3px solid #B9FF3F;outline-offset:4px}
.pu-page :is(button,select,input){font-family:"Manrope",system-ui,sans-serif}
.pu-page button:disabled,.pu-page input:disabled,.pu-page select:disabled{cursor:not-allowed}
.pu-page svg{max-width:100%}
'''
    css += "".join(".pu-page ." + cls + "{" + decl + "}\n" for decl, cls in selectors.items())
    css += '''@media(max-width:720px){.pu-page .pu-label{display:none}.pu-page .pu-h1{font-size:46px!important}.pu-page .pu-pad{padding:40px 24px!important}}
@media(max-width:430px){.pu-page .pu-h1{font-size:clamp(32px,10vw,46px)!important}.pu-page svg text{paint-order:stroke}}
'''
    return ru_out, en_out, css

def main() -> None:
    base = source_body()
    ru = normalize_markup(base, locale="ru")
    en = normalize_markup(base, locale="en")
    ru, en, css = externalize_styles(ru, en)
    expected = ["phuketravel.vercel.app", "stasph.vercel.app", "muaithaiph.vercel.app",
                "haven-ruddy.vercel.app", "rostikson-portfolio.vercel.app"]
    for locale, markup in (("ru", ru), ("en", en)):
        require(markup.count("<svg ") == base.count("<svg "), locale + ": SVG count changed")
        require(markup.count("<path ") == base.count("<path "), locale + ": SVG paths changed")
        require(markup.count("<section ") == 4 and [markup.index('id="' + name + '"') for name in ("top", "orbit", "homes", "agencies")] == sorted([markup.index('id="' + name + '"') for name in ("top", "orbit", "homes", "agencies")]), locale + ": section order changed")
        require(markup.count('rel="noopener"') == 11, locale + ": external links not protected")
        require(markup.count("<h1 ") == 1, locale + ": H1 drift")
        require('href="#orbit"' not in markup[markup.index(">Pharaohs Rawai</h3>"):markup.index("</article>", markup.index(">Pharaohs Rawai</h3>"))], locale + ": Pharaohs must not link")
        for host in expected:
            require(markup.count(f'https://{host}"') == 2, locale + ": partner link missing or added: " + host)
        require("<form " not in markup, locale + ": mock U2 filter must not submit")
    OUTPUT_MARKUP.write_text("// Generated solely from design/PHUKET-UNIVERSE-MAKET-v2.html; no runtime fetching.\n"
        "export const phuketUniverseMarkup = " + json.dumps({"ru": ru, "en": en}, ensure_ascii=False) + " as const;\n",
        encoding="utf-8", newline="\n")
    OUTPUT_CSS.write_text(css, encoding="utf-8", newline="\n")
    print(json.dumps({"source_sha256": EXPECTED_SHA256,
        "ru_characters": len(ru), "en_characters": len(en),
        "svg_per_route": base.count("<svg "), "css_classes": len(re.findall(r'\.pu-page \.pu-s\d+', css)),
        "published": False}, ensure_ascii=False))

if __name__ == "__main__":
    main()
