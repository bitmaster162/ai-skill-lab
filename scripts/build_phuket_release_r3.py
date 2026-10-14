#!/usr/bin/env python3
"""Reproduce the local R3 payload from an immutable Git parent and U1 sources.

Default is read-only comparison. --prepare-local writes only this checkout,
never a remote, and requires an explicitly Draft release profile.
"""
from __future__ import annotations
import argparse
import hashlib
import html
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy/live"
BASE = "5a6bbd6cf62425ad70b93e99237bc8c451d6ffb7"
BASE_TREE = "97bf6a47679bcfc342a133a187f30b45fd173fce"
PARENT_MANIFEST_SHA = "1c0486827cac8fceab7c2a395d3c12a47edaac56af0ecf72459cce256429e74f"
RELEASE = "PHUKET_UNIVERSE_U1_STATIC_R3_20261014"
ORIGIN = "https://aiskillab.work"
ROUTES = {"ru": "/phuket-universe", "en": "/en/phuket-universe"}


def git(*args: str) -> bytes:
    p = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, timeout=45)
    if p.returncode:
        raise RuntimeError("Git parent unavailable: " + p.stderr.decode("utf-8", "replace")[-800:])
    return p.stdout


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Scripts(HTMLParser):
    def __init__(self, text: str):
        super().__init__(convert_charrefs=False)
        self.on = False
        self.parts = []
        self.inline = []
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        if tag == "script" and "src" not in dict(attrs):
            self.on = True
            self.parts = []

    def handle_data(self, text):
        if self.on:
            self.parts.append(text)

    def handle_endtag(self, tag):
        if tag == "script" and self.on:
            self.inline.append("".join(self.parts))
            self.on = False


def parent_payload() -> dict[str, bytes]:
    if git("rev-parse", BASE + "^{tree}").decode().strip() != BASE_TREE:
        raise ValueError("Wrong immutable parent tree")
    archive = git("archive", "--format=tar", BASE, "deploy/live")
    files = {}
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for entry in tar:
            if not entry.isfile():
                if not entry.isdir():
                    raise ValueError("Non-regular Git payload entry")
                continue
            prefix = "deploy/live/"
            if not entry.name.startswith(prefix):
                raise ValueError("Unexpected archive root")
            name = entry.name[len(prefix):]
            if ".." in Path(name).parts or name in files:
                raise ValueError("Unsafe/duplicate Git path")
            stream = tar.extractfile(entry)
            if stream is None:
                raise ValueError("Missing Git archive bytes")
            files[name] = stream.read()
    manifest = files.pop("_release.json")
    if sha(manifest) != PARENT_MANIFEST_SHA:
        raise ValueError("Historical manifest SHA changed")
    m = json.loads(manifest)
    if len(files) != 98 or set(files) != {e["path"] for e in m["files"]}:
        raise ValueError("Historical inventory changed")
    for e in m["files"]:
        if (len(files[e["path"]]), sha(files[e["path"]])) != (e["size"], e["sha256"]):
            raise ValueError("Historical payload changed")
    return files


def render() -> dict[str, bytes]:
    files = parent_payload()
    src = (ROOT / "components/phuketUniverseMarkup.ts").read_text(encoding="utf-8")
    markup = json.loads(src.split("export const phuketUniverseMarkup = ", 1)[1].rsplit(" as const;", 1)[0])
    if set(markup) != {"ru", "en"}:
        raise ValueError("Exactly two locales required")
    esc = lambda text: html.escape(text, quote=True)
    for locale, route in ROUTES.items():
        source = ROOT / ("app/(ru)/phuket-universe/page.tsx" if locale == "ru" else "app/(en)/en/phuket-universe/page.tsx")
        text = source.read_text(encoding="utf-8")
        title = json.loads(re.search(r'^const title = (.*);$', text, re.M).group(1))
        desc = json.loads(re.search(r'^const description = (.*);$', text, re.M).group(1))
        if not 0 < len(title) <= 60 or not 0 < len(desc) <= 160:
            raise ValueError("U1 metadata budget")
        ld = Scripts(files[("en/" if locale == "en" else "") + "phuket.html"].decode("utf-8")).inline
        if len(ld) != 1:
            raise ValueError("Parent JSON-LD changed")
        tags = ['<!doctype html><html lang="' + locale + '"><head><meta charset="utf-8">',
                '<meta name="viewport" content="width=device-width,initial-scale=1">',
                '<title>' + esc(title) + '</title>', '<meta name="description" content="' + esc(desc) + '">',
                '<meta name="theme-color" content="#070A12">',
                '<link rel="canonical" href="' + ORIGIN + route + '">']
        for lang, path in (("ru", ROUTES["ru"]), ("en", ROUTES["en"]), ("x-default", ROUTES["ru"])):
            tags.append('<link rel="alternate" hreflang="' + lang + '" href="' + ORIGIN + path + '">')
        font_preloads = ["Unbounded-ru-en.woff2", "Manrope-latin.woff2"]
        if locale == "ru":
            font_preloads.append("Manrope-cyrillic.woff2")
        for font in font_preloads:
            tags.append('<link rel="preload" href="/fonts/' + font + '" as="font" type="font/woff2" crossorigin>')
        tags.extend(['<link rel="icon" href="/favicon.svg" type="image/svg+xml">',
                     '<link rel="icon" href="/favicon.ico" sizes="any">',
                     '<link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180">',
                     '<link rel="manifest" href="/site.webmanifest">',
                     '<link rel="stylesheet" href="/phuket-universe.css">'])
        og = {"type": "website", "site_name": "AI Skill Lab · Phuket", "locale": "en_US" if locale == "en" else "ru_RU",
              "locale:alternate": "ru_RU" if locale == "en" else "en_US", "title": title,
              "description": desc, "url": ORIGIN + route, "image": ORIGIN + "/og.png",
              "image:alt": "AI Skill Lab · Phuket", "image:width": "1200", "image:height": "630"}
        for key, value in og.items():
            tags.append('<meta property="og:' + key + '" content="' + esc(value) + '">')
        for key, value in {"card": "summary_large_image", "title": title, "description": desc, "image": ORIGIN + "/og.png"}.items():
            tags.append('<meta name="twitter:' + key + '" content="' + esc(value) + '">')
        body = ('</head><body><script type="application/ld+json">' + ld[0] + '</script>'
                + '<div class="pu-page" lang="' + locale + '" data-phuket-universe="' + locale + '">'
                + markup[locale] + '</div><script src="/lab-command.js" defer></script>'
                + '<script defer src="/_vercel/insights/script.js"></script></body></html>\n')
        files[route.lstrip("/") + ".html"] = ("".join(tags) + body).encode("utf-8")
    files["phuket-universe.css"] = b'@import url("/workshop.css");\n' + (ROOT / "app/phuket-universe.css").read_bytes()
    for name in ("Manrope-cyrillic.woff2", "Manrope-latin.woff2", "OFL-Manrope.txt"):
        files["fonts/" + name] = (ROOT / "public/fonts" / name).read_bytes()
    new_urls = "".join(f'<url><loc>{ORIGIN}{route}</loc><lastmod>2026-10-14</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>\n' for route in ROUTES.values())
    sitemap = files["sitemap.xml"].decode("utf-8")
    if sitemap.count("</urlset>") != 1:
        raise ValueError("Sitemap boundary changed")
    files["sitemap.xml"] = sitemap.replace("</urlset>", new_urls + "</urlset>").encode("utf-8")
    files["llms.txt"] += (f'\n## Phuket Universe\n- [RU]({ORIGIN}{ROUTES["ru"]}) [EN]({ORIGIN}{ROUTES["en"]})\n').encode("utf-8")
    rows = [{"path": n, "size": len(b), "sha256": sha(b)} for n, b in sorted(files.items())]
    digest = sha("".join(f"{e['path']}\t{e['size']}\t{e['sha256']}\n" for e in rows).encode("utf-8"))
    manifest = {"schema": "ai-skill-lab.static-release.v1", "release_id": RELEASE,
                "file_count": len(rows), "payload_sha256": digest, "files": rows}
    files["_release.json"] = (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode("utf-8")
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-local", action="store_true")
    args = parser.parse_args()
    files = render()
    if args.prepare_local:
        p = json.loads((ROOT / "data/phuket_universe_u1_static_r3_profile.json").read_text(encoding="utf-8"))
        if git("branch", "--show-current").decode().strip() != "agent/phuket-universe-u1-static-integration-local-r1":
            raise ValueError("Only the isolated integration branch may prepare a draft")
        if p.get("status") != "Draft" or any(p.get("authority", {}).values()):
            raise ValueError("Local draft preparation authority denied")
        for name, data in files.items():
            path = LIVE / name
            if path.is_symlink():
                raise ValueError("Symlink write target")
            if not path.exists() or path.read_bytes() != data:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
    actual = {p.relative_to(LIVE).as_posix(): p.read_bytes() for p in LIVE.rglob("*") if p.is_file()}
    if actual != files:
        raise ValueError("R3 source/static regeneration mismatch")
    print("PHUKET_R3_REPRODUCTION_PASS files=" + str(len(files)))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
