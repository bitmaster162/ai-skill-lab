#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy" / "live"
GUIDE_DIR = ROOT / "guides" / "aiskillab"
ORIGIN = "https://aiskillab.work"
ORG_ID = f"{ORIGIN}/#organization"
LASTMOD = "2026-10-05"

GUIDE_CSS = r"""
/* E2_GUIDES_START */
.guideMain{background:#f6f2e9;color:#111;min-height:60vh;padding:72px 24px 96px}
.guideListingHero,.guideCardGrid,.guideArticle{max-width:1080px;margin:0 auto}
.guideListingHero{max-width:820px;margin-bottom:42px}
.guideListingHero>span,.guideArticleHeader>span{font-family:Unbounded,system-ui,sans-serif;font-size:.75rem;letter-spacing:.12em;text-transform:uppercase}
.guideListingHero h1,.guideArticleHeader h1{font-family:Unbounded,system-ui,sans-serif;line-height:1.05;margin:12px 0 18px}
.guideListingHero h1{font-size:clamp(2.4rem,7vw,5rem)}
.guideListingHero p{max-width:66ch;font-size:1.12rem;line-height:1.6}
.guideCardGrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px}
.guideCard{background:#fff;border:1px solid #181818;padding:26px;min-width:0}
.guideCard>span{font-size:.78rem;letter-spacing:.08em;text-transform:uppercase}
.guideCard h2{font-size:1.35rem;line-height:1.25;margin:14px 0}
.guideCard h2 a,.guideCardLink{color:inherit;text-decoration-thickness:1px;text-underline-offset:4px}
.guideCard p{line-height:1.55}
.guideCardLink{display:inline-block;margin-top:14px;font-weight:700}
.guideArticle{max-width:760px}
.guideBreadcrumbs{font-size:.9rem;margin-bottom:28px}
.guideBreadcrumbs a{color:inherit}
.guideArticleHeader h1{font-size:clamp(2rem,5.2vw,3.8rem)}
.guideLead{font-size:1.18rem;line-height:1.62;max-width:66ch}
.guideReviewMeta{font-size:.9rem;font-weight:700;margin:18px 0 28px}
.guideToc{border:1px solid #181818;background:#fff;padding:22px 24px;margin:0 0 38px}
.guideToc strong{display:block;margin-bottom:10px}
.guideToc ol{margin:0;padding-left:1.35rem}
.guideToc li{margin:.35rem 0}
.guideToc a{color:inherit}
.guideBody{font-size:1.02rem;line-height:1.58;max-width:66ch;overflow-wrap:anywhere}
.guideBody h2{font-family:Unbounded,system-ui,sans-serif;font-size:clamp(1.35rem,3vw,2rem);line-height:1.2;margin:48px 0 16px;scroll-margin-top:24px}
.guideBody p{margin:0 0 18px}
.guideBody ul,.guideBody ol{padding-left:1.4rem;margin:0 0 22px}
.guideBody li{margin:.45rem 0}
.guideBody a{color:inherit;text-decoration-thickness:1px;text-underline-offset:3px}
.guideBody strong{font-weight:800}
.guideTableWrap{overflow-x:auto;max-width:100%;margin:24px 0 30px;border:1px solid #181818;background:#fff}
.guideTableWrap table{width:100%;min-width:680px;border-collapse:collapse;font-size:.94rem;line-height:1.45}
.guideTableWrap th,.guideTableWrap td{padding:12px 14px;border-bottom:1px solid #c9c2b4;border-right:1px solid #c9c2b4;text-align:left;vertical-align:top}
.guideTableWrap th{background:#ece5d8;font-weight:800}
.guideTableWrap tr:last-child td{border-bottom:0}
.guideCrosslink{max-width:1080px;margin:24px auto;padding:0 24px;font-weight:700}
.guideCrosslink a{color:inherit;text-decoration-thickness:1px;text-underline-offset:4px}
@media(max-width:640px){.guideMain{padding:44px 16px 72px}.guideCard{padding:20px}.guideArticleHeader h1{font-size:2rem}.guideLead{font-size:1.06rem}.guideToc{padding:18px}.guideBody{font-size:1rem}.guideCrosslink{padding:0 16px}}
/* E2_GUIDES_END */
""".strip()


def scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return json.loads(value)
    return value


def array(value: str) -> list[str]:
    value = value.strip()
    if not (value.startswith("[") and value.endswith("]")):
        return []
    return [scalar(item.strip()) for item in value[1:-1].split(",") if item.strip()]


def parse_guide(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n([\s\S]*?)\n---\n([\s\S]*)$", raw.replace("\r\n", "\n"))
    if not match:
        raise RuntimeError(f"frontmatter missing: {path}")
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    required = ["site", "path", "alternate", "lang", "title", "seo_title", "description", "reviewed", "next_review", "related", "schema", "research_source"]
    missing = [key for key in required if key not in values]
    if missing:
        raise RuntimeError(f"{path}: missing frontmatter {missing}")
    route = scalar(values["path"])
    slug = route.rstrip("/").split("/")[-1]
    return {
        "file": path,
        "slug": slug,
        "site": scalar(values["site"]),
        "path": route,
        "alternate": scalar(values["alternate"]),
        "lang": scalar(values["lang"]),
        "title": scalar(values["title"]),
        "seo_title": scalar(values["seo_title"]),
        "description": scalar(values["description"]),
        "reviewed": scalar(values["reviewed"]),
        "next_review": scalar(values["next_review"]),
        "related": array(values["related"]),
        "schema": array(values["schema"]),
        "research_source": scalar(values["research_source"]),
        "markdown": match.group(2).strip(),
    }


def guides() -> list[dict]:
    result = [parse_guide(p) for p in sorted(GUIDE_DIR.glob("*.md"))]
    if not result:
        raise RuntimeError("no guide markdown files")
    seen = set()
    for guide in result:
        if guide["site"] != "aiskillab.work":
            raise RuntimeError(f"wrong site in {guide['file']}")
        if guide["lang"] not in {"ru", "en"}:
            raise RuntimeError(f"unsupported lang in {guide['file']}")
        if guide["path"] in seen:
            raise RuntimeError(f"duplicate guide path {guide['path']}")
        seen.add(guide["path"])
        if set(guide["schema"]) != {"Article", "BreadcrumbList"}:
            raise RuntimeError(f"schema contract drift {guide['path']}: {guide['schema']}")
    return result


def safe_href(value: str) -> str:
    value = value.strip()
    if value.startswith("/") or value.startswith("https://") or value.startswith("http://"):
        return value
    return "#"


def inline(value: str) -> str:
    text = html.escape(value, quote=True)
    tokens: list[str] = []

    def hold(markup: str) -> str:
        token = f"@@GUIDE_TOKEN_{len(tokens)}@@"
        tokens.append(markup)
        return token

    def md_link(match: re.Match) -> str:
        label, raw_href = match.group(1), html.unescape(match.group(2))
        href = safe_href(raw_href)
        external = href.startswith(("https://", "http://"))
        attrs = ' target="_blank" rel="noopener"' if external else ""
        return hold(f'<a href="{html.escape(href, quote=True)}"{attrs}>{label}</a>')

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", md_link, text)

    url_re = re.compile(r"https?://[^\s<]+")
    def auto(match: re.Match) -> str:
        url = match.group(0)
        suffix = ""
        while url and url[-1] in ".,;:":
            suffix = url[-1] + suffix
            url = url[:-1]
        return hold(f'<a href="{url}" target="_blank" rel="noopener">{url}</a>') + suffix

    text = url_re.sub(auto, text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    for i, markup in enumerate(tokens):
        text = text.replace(f"@@GUIDE_TOKEN_{i}@@", markup)
    return text


def table_divider(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def render_markdown(markdown: str) -> dict:
    lines = markdown.replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i >= len(lines) or not lines[i].startswith("# "):
        raise RuntimeError("guide must start with h1")
    h1 = lines[i][2:].strip()
    i += 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    lead_parts = []
    while i < len(lines) and lines[i].strip() and not lines[i].startswith("## "):
        lead_parts.append(lines[i].strip())
        i += 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and re.match(r"^\*\*(Проверено|Checked)\b", lines[i].strip()):
        i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1

    toc = []
    out = []
    section = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("## "):
            section += 1
            label = line[3:].strip()
            ident = "sources" if ("источ" in label.lower() or label.lower() == "sources") else f"section-{section}"
            toc.append((ident, label))
            out.append(f'<h2 id="{ident}">{html.escape(label)}</h2>')
            i += 1
            continue
        if line.strip().startswith("|") and i + 1 < len(lines) and table_divider(lines[i + 1]):
            header = table_cells(line)
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(table_cells(lines[i]))
                i += 1
            thead = "".join(f"<th>{inline(cell)}</th>" for cell in header)
            tbody = "".join("<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in row) + "</tr>" for row in rows)
            out.append(f'<div class="guideTableWrap"><table><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table></div>')
            continue
        if re.match(r"^\d+\.\s+", line.strip()):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            out.append("<ol>" + "".join(f"<li>{inline(item)}</li>" for item in items) + "</ol>")
            continue
        if re.match(r"^-\s+", line.strip()):
            items = []
            while i < len(lines) and re.match(r"^-\s+", lines[i].strip()):
                items.append(re.sub(r"^-\s+", "", lines[i].strip()))
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline(item)}</li>" for item in items) + "</ul>")
            continue
        para = []
        while i < len(lines):
            current = lines[i]
            if not current.strip() or current.startswith("## ") or re.match(r"^\d+\.\s+", current.strip()) or re.match(r"^-\s+", current.strip()):
                break
            if current.strip().startswith("|") and i + 1 < len(lines) and table_divider(lines[i + 1]):
                break
            para.append(current.strip())
            i += 1
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
        else:
            i += 1
    return {"h1": h1, "lead": inline(" ".join(lead_parts)), "toc": toc, "body": "\n".join(out)}


RU_MONTHS = ["января","февраля","марта","апреля","мая","июня","июля","августа","сентября","октября","ноября","декабря"]
EN_MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]


def date_label(iso: str, lang: str) -> str:
    y, m, d = [int(x) for x in iso.split("-")]
    return f"{d} {(RU_MONTHS if lang == 'ru' else EN_MONTHS)[m-1]} {y}"


def route_for_file(path: Path) -> str:
    rel = path.relative_to(LIVE).as_posix()
    if rel == "index.html":
        return "/"
    if rel == "en.html":
        return "/en"
    return "/" + rel[:-5]


def output_path(route: str) -> Path:
    if route == "/":
        return LIVE / "index.html"
    if route == "/en":
        return LIVE / "en.html"
    return LIVE / f"{route.lstrip('/')}.html"


def sub_one(pattern: str, repl: str, value: str, label: str) -> str:
    result, count = re.subn(pattern, repl, value, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, got {count}")
    return result


def update_head(prefix: str, *, title: str, description: str, route: str, alternate: str, lang: str, page_type: str, image_alt: str, schemas: list[dict]) -> str:
    ru_path = route if lang == "ru" else alternate
    en_path = route if lang == "en" else alternate
    prefix = sub_one(r"<title>.*?</title>", f"<title>{html.escape(title)}</title>", prefix, "title")
    prefix = sub_one(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{html.escape(description, quote=True)}">', prefix, "description")
    prefix = sub_one(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{ORIGIN}{route}">', prefix, "canonical")
    prefix = sub_one(r'<link rel="alternate" hreflang="ru" href="[^"]*">', f'<link rel="alternate" hreflang="ru" href="{ORIGIN}{ru_path}">', prefix, "ru alternate")
    prefix = sub_one(r'<link rel="alternate" hreflang="en" href="[^"]*">', f'<link rel="alternate" hreflang="en" href="{ORIGIN}{en_path}">', prefix, "en alternate")
    if 'hreflang="x-default"' in prefix:
        prefix = sub_one(r'<link rel="alternate" hreflang="x-default" href="[^"]*">', f'<link rel="alternate" hreflang="x-default" href="{ORIGIN}{ru_path}">', prefix, "x-default")
    else:
        prefix = prefix.replace("</head>", f'<link rel="alternate" hreflang="x-default" href="{ORIGIN}{ru_path}"></head>', 1)
    prefix = sub_one(r'<meta property="og:type" content="[^"]*">', f'<meta property="og:type" content="{page_type}">', prefix, "og:type")
    prefix = sub_one(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{html.escape(title, quote=True)}">', prefix, "og:title")
    prefix = sub_one(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{html.escape(description, quote=True)}">', prefix, "og:description")
    prefix = sub_one(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{ORIGIN}{route}">', prefix, "og:url")
    prefix = sub_one(r'<meta property="og:image:alt" content="[^"]*">', f'<meta property="og:image:alt" content="{html.escape(image_alt, quote=True)}">', prefix, "og:image:alt")
    prefix = sub_one(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{html.escape(title, quote=True)}">', prefix, "twitter:title")
    prefix = sub_one(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{html.escape(description, quote=True)}">', prefix, "twitter:description")
    blocks = "".join(f'<script type="application/ld+json">{html.escape(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), quote=False)}</script>' for obj in schemas)
    return prefix.replace("</head>", blocks + "</head>", 1)


def shell(locale: str) -> tuple[str, str]:
    base = LIVE / ("en/safety.html" if locale == "en" else "safety.html")
    raw = base.read_text(encoding="utf-8")
    start = raw.index('<main id="main">')
    end = raw.index("</main>", start) + len("</main>")
    return raw[:start], raw[end:]


def organization_present(prefix: str) -> None:
    if '"@type":"EducationalOrganization"' not in prefix:
        raise RuntimeError("template missing Organization JSON-LD")


def schemas_for(guide: dict) -> list[dict]:
    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "@id": f"{ORIGIN}{guide['path']}#article",
        "headline": guide["title"],
        "description": guide["description"],
        "url": f"{ORIGIN}{guide['path']}",
        "mainEntityOfPage": f"{ORIGIN}{guide['path']}",
        "image": f"{ORIGIN}/og.png",
        "inLanguage": guide["lang"],
        "dateModified": guide["reviewed"],
        "publisher": {"@id": ORG_ID},
    }
    home = "/en" if guide["lang"] == "en" else "/"
    listing = "/en/guides" if guide["lang"] == "en" else "/guides"
    breadcrumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "@id": f"{ORIGIN}{guide['path']}#breadcrumbs",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home" if guide["lang"] == "en" else "Главная", "item": f"{ORIGIN}{home}"},
            {"@type": "ListItem", "position": 2, "name": "Guides" if guide["lang"] == "en" else "Гайды", "item": f"{ORIGIN}{listing}"},
            {"@type": "ListItem", "position": 3, "name": guide["title"], "item": f"{ORIGIN}{guide['path']}"},
        ],
    }
    return [article, breadcrumbs]


def article_main(guide: dict) -> str:
    doc = render_markdown(guide["markdown"])
    if doc["h1"] != guide["title"]:
        raise RuntimeError(f"H1/title mismatch {guide['path']}")
    en = guide["lang"] == "en"
    home = "/en" if en else "/"
    listing = "/en/guides" if en else "/guides"
    toc = "".join(f'<li><a href="#{ident}">{html.escape(label)}</a></li>' for ident, label in doc["toc"])
    review = (
        f"Checked {date_label(guide['reviewed'], 'en')} · next review {date_label(guide['next_review'], 'en')}"
        if en else
        f"Проверено {date_label(guide['reviewed'], 'ru')} · следующий пересмотр {date_label(guide['next_review'], 'ru')}"
    )
    return (
        '<main id="main" class="guideMain"><article class="guideArticle">'
        f'<nav class="guideBreadcrumbs" aria-label="{"Breadcrumbs" if en else "Хлебные крошки"}"><a href="{home}">{"Home" if en else "Главная"}</a><span> / </span><a href="{listing}">{"Guides" if en else "Гайды"}</a></nav>'
        f'<header class="guideArticleHeader"><span>{"GUIDE · AI SKILL LAB" if en else "ГАЙД · AI SKILL LAB"}</span><h1>{html.escape(doc["h1"])}</h1><p class="guideLead">{doc["lead"]}</p><p class="guideReviewMeta">{html.escape(review)}</p></header>'
        f'<nav class="guideToc" aria-label="{"Table of contents" if en else "Оглавление"}"><strong>{"Contents" if en else "Оглавление"}</strong><ol>{toc}</ol></nav>'
        f'<div class="guideBody">{doc["body"]}</div>'
        '</article></main>'
    )


def listing_main(locale: str, locale_guides: list[dict]) -> str:
    en = locale == "en"
    cards = []
    for guide in locale_guides:
        checked = f"Checked {date_label(guide['reviewed'], 'en')}" if en else f"Проверено {date_label(guide['reviewed'], 'ru')}"
        cards.append(
            f'<article class="guideCard"><span>{html.escape(checked)}</span><h2><a href="{guide["path"]}">{html.escape(guide["title"])}</a></h2>'
            f'<p>{html.escape(guide["description"])}</p><a class="guideCardLink" href="{guide["path"]}">{"Open guide →" if en else "Открыть гайд →"}</a></article>'
        )
    title = "Guides" if en else "Гайды"
    subtitle = "Short, checked guides for parents, adult learners and teams. Each one shows when it was checked and its sources." if en else "Короткие проверенные материалы для родителей, взрослых учеников и команд. У каждого — дата проверки и источники."
    return (
        '<main id="main" class="guideMain">'
        f'<section class="guideListingHero"><span>{"GUIDES · CHECKED SOURCES" if en else "ГАЙДЫ · ПРОВЕРЕННЫЕ ИСТОЧНИКИ"}</span><h1>{title}</h1><p>{html.escape(subtitle)}</p></section>'
        f'<section class="guideCardGrid" aria-label="{"Published guides" if en else "Опубликованные гайды"}">{"".join(cards)}</section>'
        '</main>'
    )


def build_page(locale: str, *, title: str, description: str, route: str, alternate: str, page_type: str, image_alt: str, main: str, schemas: list[dict] | None = None) -> str:
    prefix, suffix = shell(locale)
    organization_present(prefix)
    if locale == "en":
        old_switch = '<a class="workshopUtility" href="/safety">RU</a>'
        new_switch = f'<a class="workshopUtility" href="{alternate}">RU</a>'
    else:
        old_switch = '<a class="workshopUtility" href="/en/safety">EN</a>'
        new_switch = f'<a class="workshopUtility" href="{alternate}">EN</a>'
    if prefix.count(old_switch) != 1:
        raise RuntimeError(f"language switch template drift for {route}: count={prefix.count(old_switch)}")
    prefix = prefix.replace(old_switch, new_switch, 1)
    prefix = update_head(prefix, title=title, description=description, route=route, alternate=alternate, lang=locale, page_type=page_type, image_alt=image_alt, schemas=schemas or [])
    return prefix + main + suffix


def ensure_footer_links() -> int:
    changed = 0
    for page in sorted(LIVE.rglob("*.html")):
        if page.name == "404.html":
            continue
        raw = page.read_text(encoding="utf-8")
        route = route_for_file(page)
        en = route == "/en" or route.startswith("/en/")
        anchor = '<a href="/en/faq">FAQ</a>' if en else '<a href="/faq">FAQ</a>'
        guide = '<a href="/en/guides">Guides</a>' if en else '<a href="/guides">Гайды</a>'
        if anchor + guide in raw:
            continue
        if anchor not in raw:
            raise RuntimeError(f"{route}: footer FAQ anchor missing")
        page.write_text(raw.replace(anchor, anchor + guide, 1), encoding="utf-8", newline="\n")
        changed += 1
    return changed


def ensure_crosslinks() -> int:
    mapping = {
        "kids.html": ("/guides/ai-safety-for-kids", "Чек-лист для родителей: возраст, данные, родительский контроль →"),
        "parents.html": ("/guides/ai-safety-for-kids", "Чек-лист для родителей: возраст, данные, родительский контроль →"),
        "safety.html": ("/guides/ai-safety-for-kids", "Чек-лист для родителей: возраст, данные, родительский контроль →"),
        "en/kids.html": ("/en/guides/ai-safety-for-kids", "Parent checklist: age rules, data, parental controls →"),
        "en/parents.html": ("/en/guides/ai-safety-for-kids", "Parent checklist: age rules, data, parental controls →"),
        "en/safety.html": ("/en/guides/ai-safety-for-kids", "Parent checklist: age rules, data, parental controls →"),
    }
    changed = 0
    for rel, (href, label) in mapping.items():
        page = LIVE / rel
        raw = page.read_text(encoding="utf-8")
        marker = 'data-guide-crosslink="e2"'
        if marker in raw:
            continue
        pos = raw.rfind("</main>")
        if pos < 0:
            raise RuntimeError(f"{rel}: main closing tag missing")
        block = f'<p class="guideCrosslink" data-guide-crosslink="e2"><a href="{href}">{html.escape(label)}</a></p>'
        page.write_text(raw[:pos] + block + raw[pos:], encoding="utf-8", newline="\n")
        changed += 1
    return changed


def update_css() -> None:
    path = LIVE / "workshop.css"
    raw = path.read_text(encoding="utf-8")
    pattern = re.compile(r"/\* E2_GUIDES_START \*/[\s\S]*?/\* E2_GUIDES_END \*/")
    if pattern.search(raw):
        raw = pattern.sub(GUIDE_CSS, raw)
    else:
        raw = raw.rstrip() + "\n" + GUIDE_CSS + "\n"
    path.write_text(raw, encoding="utf-8", newline="\n")


def update_sitemap() -> int:
    routes = sorted(route_for_file(p) for p in LIVE.rglob("*.html") if p.name != "404.html")
    urls = "".join(f"<url><loc>{ORIGIN}{'/' if route == '/' else route}</loc><lastmod>{LASTMOD}</lastmod></url>" for route in routes)
    (LIVE / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n', encoding="utf-8", newline="\n")
    return len(routes)


def update_llms(all_guides: list[dict]) -> int:
    path = LIVE / "llms.txt"
    raw = path.read_text(encoding="utf-8")
    raw = re.sub(r"\n+## Guides\n[\s\S]*?(?=\n+## About\n)", "", raw)
    raw = re.sub(r"\n+## About\n", "\n\n## About\n", raw, count=1)
    pairs: dict[str, dict[str, str]] = {}
    for guide in all_guides:
        pairs.setdefault(guide["slug"], {})[guide["lang"]] = guide["path"]
    lines = ["## Guides", f"- [RU]({ORIGIN}/guides) [EN]({ORIGIN}/en/guides)"]
    for slug in sorted(pairs):
        pair = pairs[slug]
        if set(pair) != {"ru", "en"}:
            raise RuntimeError(f"guide locale pair incomplete: {slug}")
        lines.append(f"- [RU]({ORIGIN}{pair['ru']}) [EN]({ORIGIN}{pair['en']})")
    section = "\n".join(lines)
    marker = "\n\n## About\n"
    if marker not in raw:
        raise RuntimeError("llms About marker missing")
    raw = raw.replace(marker, "\n\n" + section + "\n\n## About\n", 1)
    path.write_text(raw, encoding="utf-8", newline="\n")
    urls = re.findall(r"\]\((https?://[^)]+)\)", raw)
    return len(urls)


def main() -> int:
    all_guides = guides()
    by_lang = {lang: [g for g in all_guides if g["lang"] == lang] for lang in ("ru", "en")}
    if any(not by_lang[lang] for lang in by_lang):
        raise RuntimeError("both locales require at least one guide")

    # Generate listing pages first.
    listing_meta = {
        "ru": ("Гайды | AI Skill Lab · Phuket", "Короткие проверенные материалы для родителей, взрослых учеников и команд. У каждого — дата проверки и источники.", "/guides", "/en/guides"),
        "en": ("Guides | AI Skill Lab · Phuket", "Short, checked guides for parents, adult learners and teams. Each one shows when it was checked and its sources.", "/en/guides", "/guides"),
    }
    for lang in ("ru", "en"):
        title, desc, route, alt = listing_meta[lang]
        page = build_page(lang, title=title, description=desc, route=route, alternate=alt, page_type="website", image_alt="AI Skill Lab · Phuket", main=listing_main(lang, by_lang[lang]))
        out = output_path(route)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8", newline="\n")

    # Generate article pages from Markdown.
    for guide in all_guides:
        page = build_page(
            guide["lang"],
            title=guide["seo_title"],
            description=guide["description"],
            route=guide["path"],
            alternate=guide["alternate"],
            page_type="article",
            image_alt="AI Skill Lab · Phuket",
            main=article_main(guide),
            schemas=schemas_for(guide),
        )
        out = output_path(guide["path"])
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8", newline="\n")

    footer_changes = ensure_footer_links()
    crosslink_changes = ensure_crosslinks()
    update_css()
    route_count = update_sitemap()
    llms_urls = update_llms(all_guides)

    print(f"E2_GUIDE_BUILD_PASS guides={len(all_guides)} listings=2 public_routes={route_count} llms_urls={llms_urls} footer_changes={footer_changes} crosslink_changes={crosslink_changes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
