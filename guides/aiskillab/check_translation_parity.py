#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
GUIDES = ROOT / "guides" / "aiskillab"
README = GUIDES / "README.md"
REQUIRED_E2_FIELDS = (
    "site", "path", "alternate", "lang", "title", "seo_title", "description",
    "reviewed", "next_review", "related", "schema", "research_source",
)

MONTHS = {
    "january": 1, "jan": 1, "января": 1,
    "february": 2, "feb": 2, "февраля": 2,
    "march": 3, "mar": 3, "марта": 3,
    "april": 4, "apr": 4, "апреля": 4,
    "may": 5, "мая": 5,
    "june": 6, "jun": 6, "июня": 6,
    "july": 7, "jul": 7, "июля": 7,
    "august": 8, "aug": 8, "августа": 8,
    "september": 9, "sep": 9, "sept": 9, "сентября": 9,
    "october": 10, "oct": 10, "октября": 10,
    "november": 11, "nov": 11, "ноября": 11,
    "december": 12, "dec": 12, "декабря": 12,
}
MONTH_PATTERN = "|".join(sorted((re.escape(x) for x in MONTHS), key=len, reverse=True))
DATE_WORD_RE = re.compile(rf"(?<!\d)(\d{{1,2}})\s+({MONTH_PATTERN})\s+(\d{{4}})(?!\d)", re.I)
DATE_DOT_RE = re.compile(r"(?<!\d)(\d{1,2})[./](\d{1,2})[./](\d{4})(?!\d)")
DATE_ISO_RE = re.compile(r"(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)")
HEADING_RE = re.compile(r"^(#{2,3})\s+\S", re.M)
LIST_RE = re.compile(r"^\s*(?:[-+*]|\d+[.)])\s+\S", re.M)
MARKDOWN_URL_RE = re.compile(r"\]\(([^)\s]+)")
BARE_URL_RE = re.compile(r"https?://[^\s<>()\]\[\"']+")
NUMBER_RE = re.compile(r"(?<![\w])\d+(?:[.,]\d+)?(?![\w])")


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing frontmatter")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise ValueError("unterminated frontmatter") from exc
    data: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data, "\n".join(lines[end + 1 :])


def required_metadata_errors(slug: str, lang: str, data: dict[str, str]) -> list[str]:
    """Reject a translation pair whose metadata would fail the E2 source contract."""
    errors: list[str] = []
    for field in REQUIRED_E2_FIELDS:
        if not data.get(field, "").strip():
            errors.append(f"{slug}: {lang} missing/empty required E2 field {field}")
    for field in ("reviewed", "next_review"):
        value = data.get(field, "")
        if value and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            errors.append(f"{slug}: {lang} invalid {field} date {value}")
    for field in ("related", "schema"):
        value = data.get(field, "")
        if value and not (value.startswith("[") and value.endswith("]")):
            errors.append(f"{slug}: {lang} invalid E2 list field {field}")
    schema = data.get("schema", "")
    if schema.startswith("[") and schema.endswith("]"):
        actual = {value.strip() for value in schema[1:-1].split(",") if value.strip()}
        if actual != {"Article", "BreadcrumbList"}:
            errors.append(f"{slug}: {lang} unexpected schema types {sorted(actual)}")
    return errors


def english_without_russian(ru_files: list[Path], en_files: list[Path]) -> list[str]:
    ru_slugs = {path.name.removesuffix(".ru.md") for path in ru_files}
    return sorted(
        path.name.removesuffix(".en.md")
        for path in en_files
        if path.name.removesuffix(".en.md") not in ru_slugs
    )


def normalise_dates(text: str) -> str:
    def word(match: re.Match[str]) -> str:
        day = int(match.group(1))
        month = MONTHS[match.group(2).lower()]
        year = int(match.group(3))
        return f"{year:04d}-{month:02d}-{day:02d}"

    def dotted(match: re.Match[str]) -> str:
        day, month, year = map(int, match.groups())
        return f"{year:04d}-{month:02d}-{day:02d}"

    text = DATE_WORD_RE.sub(word, text)
    text = DATE_DOT_RE.sub(dotted, text)
    return text


def table_rows(body: str) -> int:
    count = 0
    for line in body.splitlines():
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells):
            continue
        count += 1
    return count


def structure(body: str) -> dict[str, int]:
    headings = Counter(m.group(1) for m in HEADING_RE.finditer(body))
    return {
        "h2": headings["##"],
        "h3": headings["###"],
        "table_rows": table_rows(body),
        "list_items": len(LIST_RE.findall(body)),
    }


def frontmatter_internal_urls(frontmatter: dict[str, str]) -> set[str]:
    urls: set[str] = set()
    for key in ("path", "alternate", "related"):
        value = frontmatter.get(key, "")
        urls.update(re.findall(r"/(?:en/)?[A-Za-z0-9][^\s,\]\}\"']*", value))
    return urls


def normalise_internal_path(path: str) -> str:
    if path == "/en":
        return "/"
    if path.startswith("/en/"):
        return path[3:] or "/"
    return path


def normalise_url(raw: str) -> str:
    value = raw.rstrip(".,;:")
    if value.startswith("/"):
        parts = urlsplit(value)
        return urlunsplit(("", "", normalise_internal_path(parts.path), parts.query, parts.fragment))
    parts = urlsplit(value)
    if parts.scheme in {"http", "https"} and parts.netloc.lower() in {"aiskillab.work", "www.aiskillab.work"}:
        path = normalise_internal_path(parts.path or "/")
        return urlunsplit((parts.scheme.lower(), "aiskillab.work", path, parts.query, parts.fragment))
    return value


def url_set(text: str, frontmatter: dict[str, str]) -> set[str]:
    found = set(MARKDOWN_URL_RE.findall(text))
    found.update(BARE_URL_RE.findall(text))
    found.update(frontmatter_internal_urls(frontmatter))
    return {normalise_url(x) for x in found}


def number_set(text: str) -> set[str]:
    normalised = normalise_dates(text)
    return {token.replace(",", ".") for token in NUMBER_RE.findall(normalised)}


def require_readme(errors: list[str]) -> None:
    if not README.is_file():
        errors.append("missing guides/aiskillab/README.md")
        return
    text = README.read_text(encoding="utf-8")
    required = [
        "Translation rules · T1.2",
        "British spelling",
        "Do not add or remove facts, numbers, dates, examples, sources, caveats or disclaimers.",
        "python guides/aiskillab/check_translation_parity.py",
        "T1_4_TRANSLATION_PARITY_PASS",
    ]
    for marker in required:
        if marker not in text:
            errors.append(f"README missing contract marker: {marker}")


def compare_pair(ru_path: Path, en_path: Path) -> tuple[dict[str, int], list[str]]:
    errors: list[str] = []
    ru_text = ru_path.read_text(encoding="utf-8")
    en_text = en_path.read_text(encoding="utf-8")
    try:
        ru_fm, ru_body = split_frontmatter(ru_text)
        en_fm, en_body = split_frontmatter(en_text)
    except ValueError as exc:
        return {}, [f"{ru_path.stem}: {exc}"]

    slug = ru_path.name.removesuffix(".ru.md")
    errors.extend(required_metadata_errors(slug, "ru", ru_fm))
    errors.extend(required_metadata_errors(slug, "en", en_fm))
    expected_ru = f"/guides/{slug}"
    expected_en = f"/en/guides/{slug}"
    contracts = [
        (ru_fm.get("site") == "aiskillab.work" == en_fm.get("site"), "site"),
        (ru_fm.get("lang") == "ru" and en_fm.get("lang") == "en", "lang"),
        (ru_fm.get("path") == expected_ru and ru_fm.get("alternate") == expected_en, "RU path/alternate"),
        (en_fm.get("path") == expected_en and en_fm.get("alternate") == expected_ru, "EN path/alternate"),
    ]
    for field in ("reviewed", "next_review", "schema"):
        contracts.append((ru_fm.get(field) == en_fm.get(field), field))
    if "sources" in ru_fm or "sources" in en_fm:
        contracts.append((ru_fm.get("sources") == en_fm.get("sources"), "sources"))
    for ok, label in contracts:
        if not ok:
            errors.append(f"{slug}: frontmatter mismatch {label}")

    ru_struct = structure(ru_body)
    en_struct = structure(en_body)
    for key in ("h2", "h3", "table_rows", "list_items"):
        if ru_struct[key] != en_struct[key]:
            errors.append(f"{slug}: {key} RU={ru_struct[key]} EN={en_struct[key]}")

    ru_urls = url_set(ru_text, ru_fm)
    en_urls = url_set(en_text, en_fm)
    if ru_urls != en_urls:
        errors.append(f"{slug}: URL mismatch RU_only={sorted(ru_urls-en_urls)} EN_only={sorted(en_urls-ru_urls)}")

    ru_numbers = number_set(ru_text)
    en_numbers = number_set(en_text)
    if ru_numbers != en_numbers:
        errors.append(f"{slug}: number mismatch RU_only={sorted(ru_numbers-en_numbers)} EN_only={sorted(en_numbers-ru_numbers)}")

    stats = {
        **ru_struct,
        "urls": len(ru_urls),
        "numbers": len(ru_numbers),
    }
    return stats, errors


def main() -> int:
    errors: list[str] = []
    require_readme(errors)
    ru_files = sorted(GUIDES.glob("*.ru.md"))
    en_files = sorted(GUIDES.glob("*.en.md"))
    if not ru_files:
        errors.append("no RU guide sources found")
    for slug in english_without_russian(ru_files, en_files):
        errors.append(f"{slug}: missing RU pair")

    pairs = 0
    for ru_path in ru_files:
        slug = ru_path.name.removesuffix(".ru.md")
        en_path = GUIDES / f"{slug}.en.md"
        if not en_path.is_file():
            errors.append(f"{slug}: missing EN pair")
            continue
        pairs += 1
        stats, pair_errors = compare_pair(ru_path, en_path)
        errors.extend(pair_errors)
        if stats:
            print(
                f"T1_4_PAIR slug={slug} h2={stats['h2']} h3={stats['h3']} "
                f"table_rows={stats['table_rows']} list_items={stats['list_items']} "
                f"urls={stats['urls']} numbers={stats['numbers']} mismatches={len(pair_errors)}"
            )

    if errors:
        print(f"T1_4_TRANSLATION_PARITY_FAIL pairs={pairs} mismatches={len(errors)}")
        for error in errors:
            print("-", error)
        return 1
    print(f"T1_4_TRANSLATION_PARITY_PASS pairs={pairs} mismatches=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
