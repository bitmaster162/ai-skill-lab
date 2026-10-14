#!/usr/bin/env python3
"""Prepare a create-only LOCAL U1 static candidate; never mutate deploy/live.

Existing source and payload are pinned to merged PR229. The new release ID is
candidate-only. Publication gates and unresolved author copy remain HOLD.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "5a6bbd6cf62425ad70b93e99237bc8c451d6ffb7"
BASE_TREE = "97bf6a47679bcfc342a133a187f30b45fd173fce"
BASE_MANIFEST = "1c0486827cac8fceab7c2a395d3c12a47edaac56af0ecf72459cce256429e74f"
BASE_PAYLOAD = "188c0b7c3204dd4c1366a51facafeb09421c929e58913e34c7500d9fdf2ea30e"
RELEASE = "PHUKET_UNIVERSE_U1_STATIC_CANDIDATE_R1_20261014"
OUT = ROOT / "deploy/preview" / RELEASE
ORIGIN = "https://aiskillab.work"
ROUTES = {"ru": "/phuket-universe", "en": "/en/phuket-universe"}
NEW_FILES = frozenset({"phuket-universe.html", "en/phuket-universe.html",
    "phuket-universe.css", "fonts/Manrope-cyrillic.woff2",
    "fonts/Manrope-latin.woff2", "fonts/OFL-Manrope.txt"})
EDITED_PARENT_FILES = frozenset({"sitemap.xml", "llms.txt"})
INPUTS = (
    "components/phuketUniverseMarkup.ts", "app/phuket-universe.css",
    "app/(ru)/phuket-universe/page.tsx", "app/(en)/en/phuket-universe/page.tsx",
    "public/fonts/Manrope-cyrillic.woff2", "public/fonts/Manrope-latin.woff2",
    "public/fonts/OFL-Manrope.txt", "design/PHUKET-UNIVERSE-MAKET-v2.html",
)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git(*args: str) -> str:
    p = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=30)
    need(p.returncode == 0, "Git verification failed: " + p.stderr[-800:])
    return p.stdout.strip()


def safe_path(name: str) -> bool:
    p = PurePosixPath(name)
    return bool(name) and not p.is_absolute() and ".." not in p.parts and "\\" not in name and ":" not in name


def file_index(files: dict[str, bytes]) -> list[dict]:
    return [{"path": n, "size": len(b), "sha256": sha(b)} for n, b in sorted(files.items())]


def payload_digest(entries: list[dict]) -> str:
    text = "".join(f"{v['path']}\t{v['size']}\t{v['sha256']}\n" for v in sorted(entries, key=lambda v: v['path']))
    return sha(text.encode("utf-8"))


def verify_manifest(files: dict[str, bytes], raw: bytes) -> dict:
    m = json.loads(raw)
    need(m.get("schema") == "ai-skill-lab.static-release.v1", "Invalid manifest schema")
    entries = m.get("files", [])
    need(all(safe_path(e["path"]) for e in entries), "Unsafe manifest path")
    need(len({e["path"] for e in entries}) == len(entries), "Duplicate manifest paths")
    need(m.get("file_count") == len(files) == len(entries), "Manifest count mismatch")
    need(sorted(entries, key=lambda v: v['path']) == file_index(files), "Payload bytes differ from manifest")
    need(payload_digest(entries) == m.get("payload_sha256"), "Payload digest mismatch")
    return m


class Page(HTMLParser):
    def __init__(self, text: str):
        super().__init__(convert_charrefs=False)
        self.tags: list[tuple[str, dict]] = []
        self.inline: list[str] = []
        self.canonical: list[str] = []
        self.alternates: dict[str, str] = {}
        self._in_script = False
        self._chunks: list[str] = []
        self.feed(text)
        self.close()

    def handle_starttag(self, tag: str, attrs: list) -> None:
        a = dict(attrs)
        self.tags.append((tag, a))
        if tag == "script" and "src" not in a:
            self._in_script = True
            self._chunks = []
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical.append(a.get("href"))
        if tag == "link" and a.get("rel") == "alternate":
            self.alternates[a.get("hreflang")] = a.get("href")

    def handle_data(self, data: str) -> None:
        if self._in_script:
            self._chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._in_script:
            self.inline.append("".join(self._chunks))
            self._in_script = False


def parent_payload() -> dict[str, bytes]:
    live = ROOT / "deploy/live"
    raw = (live / "_release.json").read_bytes()
    need(sha(raw) == BASE_MANIFEST, "Historical manifest drift")
    m = json.loads(raw)
    need(m.get("payload_sha256") == BASE_PAYLOAD, "Historical payload drift")
    need(m.get("release_id") == "T1_6F2_ADULT_FIRST_TASKS_R1", "Wrong parent release")
    need(all(safe_path(e["path"]) for e in m["files"]), "Unsafe parent path")
    files = {}
    for e in m["files"]:
        p = live / e["path"]
        need(not p.is_symlink() and p.resolve().is_relative_to(live.resolve()), "Unsafe parent file")
        files[e["path"]] = p.read_bytes()
    actual = {p.relative_to(live).as_posix() for p in live.rglob("*") if p.is_file() and p.name != "_release.json"}
    need(actual == set(files), "Historical directory inventory drift")
    verify_manifest(files, raw)
    need(len(files) == 98, "Parent must contain 98 payload files")
    return files


def source_inputs() -> dict[str, bytes]:
    need(git("rev-parse", BASE + "^{tree}") == BASE_TREE, "Wrong Git base")
    need(not git("diff", BASE, "--name-only", "--", *INPUTS, "deploy/live"), "Reviewed source changed")
    inputs = {}
    for name in INPUTS:
        p = ROOT / name
        need(not p.is_symlink() and p.resolve().is_relative_to(ROOT.resolve()), "Unsafe source path")
        inputs[name] = p.read_bytes()
    need(sha(inputs["design/PHUKET-UNIVERSE-MAKET-v2.html"]) == "2d5112f138e7364a83b15471179b5767891e3448e188f0f566d139702dd97024", "Design source drift")
    return inputs


def route_metadata(raw: bytes) -> tuple[str, str]:
    text = raw.decode("utf-8")
    values = []
    for name, limit in (("title", 60), ("description", 160)):
        matches = re.findall(r'^const ' + name + r' = ("(?:[^"\\]|\\.)*");$', text, re.M)
        need(len(matches) == 1, "Ambiguous source metadata: " + name)
        value = json.loads(matches[0])
        need(0 < len(value) <= limit, "Source metadata length: " + name)
        values.append(value)
    return values[0], values[1]


def render() -> tuple[dict[str, bytes], dict]:
    files = parent_payload()
    parent = files.copy()
    inputs = source_inputs()
    ts = inputs["components/phuketUniverseMarkup.ts"].decode("utf-8")
    prefix = "export const phuketUniverseMarkup = "
    need(ts.count(prefix) == 1 and ts.rstrip().endswith(" as const;"), "Malformed reviewed markup")
    markup = json.loads(ts.split(prefix, 1)[1].rsplit(" as const;", 1)[0])
    need(set(markup) == {"ru", "en"}, "Exactly two locales required")
    esc = lambda v: html.escape(v, quote=True)
    for locale, route in ROUTES.items():
        source = "app/(ru)/phuket-universe/page.tsx" if locale == "ru" else "app/(en)/en/phuket-universe/page.tsx"
        title, desc = route_metadata(inputs[source])
        parent_page = Page(parent[("en/" if locale == "en" else "") + "phuket.html"].decode("utf-8"))
        need(len(parent_page.inline) == 1, "Unexpected parent inline scripts")
        ld = parent_page.inline[0]
        need(json.loads(ld).get("@type") == "EducationalOrganization", "Wrong parent JSON-LD")
        head = (f'<!doctype html><html lang="{locale}"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                f'<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">'
                '<meta name="theme-color" content="#070A12">'
                f'<link rel="canonical" href="{ORIGIN}{route}">')
        for lang, path in (("ru", ROUTES["ru"]), ("en", ROUTES["en"]), ("x-default", ROUTES["ru"])):
            head += f'<link rel="alternate" hreflang="{lang}" href="{ORIGIN}{path}">'
        head += ('<link rel="icon" href="/favicon.svg" type="image/svg+xml">'
                 '<link rel="manifest" href="/site.webmanifest">'
                 '<link rel="stylesheet" href="/phuket-universe.css">'
                 f'<meta property="og:title" content="{esc(title)}">'
                 f'<meta property="og:description" content="{esc(desc)}">'
                 f'<meta property="og:url" content="{ORIGIN}{route}">'
                 '<meta property="og:type" content="website">'
                 '<meta property="og:site_name" content="AI Skill Lab">'
                 f'<meta property="og:locale" content="{"en_US" if locale == "en" else "ru_RU"}">'
                 '</head><body>')
        doc = (head + f'<script type="application/ld+json">{ld}</script>'
               f'<div class="pu-page" lang="{locale}" data-phuket-universe="{locale}">'
               + markup[locale] + '</div><script src="/lab-command.js" defer></script>'
               '<script defer src="/_vercel/insights/script.js"></script></body></html>\n')
        files[route.lstrip("/") + ".html"] = doc.encode("utf-8")
    files["phuket-universe.css"] = b'@import url("/workshop.css");\n' + inputs["app/phuket-universe.css"]
    for font in ("Manrope-cyrillic.woff2", "Manrope-latin.woff2", "OFL-Manrope.txt"):
        files["fonts/" + font] = inputs["public/fonts/" + font]
    sitemap = parent["sitemap.xml"].decode("utf-8")
    need(sitemap.count("</urlset>") == 1, "Unexpected sitemap boundary")
    new_urls = "".join(f'<url><loc>{ORIGIN}{route}</loc><lastmod>2026-10-14</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>\n' for route in ROUTES.values())
    files["sitemap.xml"] = sitemap.replace("</urlset>", new_urls + "</urlset>").encode("utf-8")
    files["llms.txt"] += (f'\n## Phuket Universe\n- [RU]({ORIGIN}{ROUTES["ru"]}) [EN]({ORIGIN}{ROUTES["en"]})\n').encode("utf-8")
    need(set(files) - set(parent) == NEW_FILES, "New-file scope changed")
    need({n for n in parent if parent[n] != files[n]} == EDITED_PARENT_FILES, "Parent modification scope changed")
    entries = file_index(files)
    manifest = {"schema": "ai-skill-lab.static-release.v1", "release_id": RELEASE,
                "file_count": len(files), "payload_sha256": payload_digest(entries), "files": entries}
    manifest_raw = (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode("utf-8")
    verify_manifest(files, manifest_raw)
    stats = validate_pages(files, markup)
    font_bytes = sum(len(b) for n, b in files.items() if n.endswith(".woff2"))
    non_font_bytes = sum(len(b) for n, b in files.items() if not n.endswith(".woff2"))
    stats.update({"release_id": RELEASE, "parent_base": BASE, "parent_manifest_sha256": BASE_MANIFEST,
                  "manifest_sha256": sha(manifest_raw), "payload_sha256": manifest["payload_sha256"],
                  "file_count": len(files), "parent_files_unchanged": 96,
                  "modified_parent_files": sorted(EDITED_PARENT_FILES), "new_files": sorted(NEW_FILES),
                  "font_count": sum(n.endswith(".woff2") for n in files), "font_bytes": font_bytes,
                  "non_font_bytes": non_font_bytes, "payload_bytes": font_bytes + non_font_bytes,
                  "payload_delta_bytes": font_bytes + non_font_bytes - sum(map(len, parent.values())),
                  "parent_font_limit_bytes": 84 * 1024, "parent_non_font_limit_bytes": 1120 * 1024,
                  "source_sha256": {n: sha(b) for n, b in inputs.items()},
                  "release_authorized": False, "deploy_authorized": False,
                  "production_ready": False, "existing_E3_8_script_unchanged": True,
                  "publication_holds": ["NEW_RELEASE_PROFILE_NOT_REGISTERED",
                      "FOUR_FONTS_EXCEED_EXISTING_TWO_FONT_CONTRACT",
                      "PAYLOAD_EXCEEDS_PARENT_RELEASE_BUDGET",
                      "SOURCE_AGENCY_TERMS_PLACEHOLDER_UNRESOLVED",
                      "U2_U3_AND_NEW_UNIVERSE_EVENTS_NOT_INCLUDED"]})
    files["_release.json"] = manifest_raw
    return files, stats


def validate_pages(files: dict[str, bytes], markup: dict[str, str]) -> dict:
    old = parent_payload()
    need(files["vercel.json"] == old["vercel.json"], "CSP/config must remain byte-identical")
    cfg = json.loads(files["vercel.json"])
    csp = next(h["value"] for rule in cfg["headers"] if rule["source"] == "/(.*)" for h in rule["headers"] if h["key"] == "Content-Security-Policy")
    pages = {}
    for n, data in files.items():
        if not n.endswith(".html") or n == "404.html":
            continue
        route = "/" if n == "index.html" else "/" + n[:-5]
        pages[route] = Page(data.decode("utf-8"))
    need(len(pages) == 56, "Candidate must contain 56 public routes")
    urls = [e.text for e in ET.fromstring(files["sitemap.xml"]).findall("{*}url/{*}loc")]
    need(len(urls) == len(set(urls)) == 56 and set(urls) == {ORIGIN + route for route in pages}, "Candidate sitemap mismatch")
    for locale, route in ROUTES.items():
        p = pages[route]
        text = files[route.lstrip("/") + ".html"].decode("utf-8")
        need(markup[locale] in text, "Reviewed body changed")
        need(p.canonical == [ORIGIN + route], "Canonical mismatch")
        need(p.alternates == {"ru": ORIGIN + ROUTES["ru"], "en": ORIGIN + ROUTES["en"], "x-default": ORIGIN + ROUTES["ru"]}, "Hreflang mismatch")
        need(sum(t == "h1" for t, _ in p.tags) == 1, "H1 mismatch")
        need([a.get("id") for t, a in p.tags if t == "section"] == ["top", "orbit", "homes", "agencies"], "Section order changed")
        need(sum(t == "svg" for t, _ in p.tags) == 8, "SVG count mismatch")
        need(not any("style" in a or t == "style" for t, a in p.tags), "Inline styles are not allowed")
        need(not any(t == "form" for t, _ in p.tags), "U2 filter must not submit")
        need(all("disabled" in a for t, a in p.tags if t in {"input", "button", "select"}), "U2 controls not fail-closed")
        for script in p.inline:
            digest = "'sha256-" + base64.b64encode(hashlib.sha256(script.encode("utf-8")).digest()).decode("ascii") + "'"
            need(digest in csp, "New inline hash would require CSP mutation")
        for tag, a in p.tags:
            if tag == "a" and a.get("href", "").startswith("https://"):
                need("noopener" in a.get("rel", "").split(), "External link lacks noopener")
    return {"candidate_structural_checks": "PASS", "public_routes": len(pages), "sitemap_routes": len(urls), "csp_byte_identical": True}


def write_candidate(files: dict[str, bytes]) -> None:
    need(not git("status", "--porcelain=v1"), "Commit and clean source before sealing candidate")
    need(not OUT.exists(), "Candidate already exists; no overwrite or silent reseal")
    need(OUT.parent.resolve().is_relative_to(ROOT.resolve()), "Unsafe output parent")
    OUT.mkdir(parents=True, exist_ok=False)
    for name, data in sorted(files.items(), key=lambda x: x[0] == "_release.json"):
        need(safe_path(name), "Unsafe output file")
        p = OUT / name
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("xb") as stream:
            stream.write(data)
    actual = {p.relative_to(OUT).as_posix(): p.read_bytes() for p in OUT.rglob("*") if p.is_file()}
    need(actual == files, "Written candidate differs; STOP without cleanup or retry")
    print("CANDIDATE_WRITTEN", str(OUT), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-candidate", action="store_true")
    args = parser.parse_args()
    files, stats = render()
    if args.write_candidate:
        write_candidate(files)
    print(json.dumps(stats, ensure_ascii=False, sort_keys=True, indent=2), flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
