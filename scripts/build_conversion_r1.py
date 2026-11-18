"""Build the reviewable Conversion R1 static site into a new directory."""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import re
from pathlib import Path
from tempfile import TemporaryDirectory

import build_guides as guides

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy" / "live"
PARENT = "79ecdcd892a308ef3ae93b6f551a4c01e59e9a584eee39764daba5498df11889"
RELEASE = "CONVERSION_R1_20261118"
NEW_GUIDES = ("ai-pilot-for-small-business", "ai-start-for-adults")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def replace_one(text: str, pattern: str, value: str) -> str:
    result, count = re.subn(pattern, lambda _: value, text, flags=re.S)
    if count != 1:
        raise ValueError(f"Expected one match for {pattern!r}, found {count}")
    return result


def build_home(out: Path, lang: str, copy: dict) -> None:
    prefix = "/en" if lang == "en" else ""
    page = out / ("en.html" if prefix else "index.html")
    text = page.read_text(encoding="utf-8")
    text = replace_one(text, r'(<div class="heroCopy"><span class="eyebrow">[^<]+</span>)<h1>.*?</h1><p>.*?</p>',
                       re.search(r'<div class="heroCopy"><span class="eyebrow">[^<]+</span>', text)[0]
                       + f'<h1>{copy["heading"]}</h1><p>{copy["intro"]}</p>')
    form = f'{prefix}/start#application-form'
    anchor = f'<a class="workshopButton workshopButtonPrimary" href="{form}">{copy["apply"]} →</a>'
    text = replace_one(text, rf'<div class="heroActions"><a class="workshopButton workshopButtonPrimary" href="{prefix}/start">',
                       f'<div class="heroActions"><a class="workshopButton workshopButtonPrimary" href="{prefix}/matcher">')
    text = replace_one(text, rf'<a class="workshopButton workshopButtonPrimary" href="{prefix}/start">(?:Начать|Start) →</a>', anchor)
    pricing = re.escape(f'<a class="workshopButton workshopButtonDark" href="{prefix}/pricing">') + r'[^<]+</a>'
    pricing_cta = re.search(pricing, text)[0]
    text = replace_one(text, pricing, pricing_cta + f'<a class="workshopButton workshopButtonSecondary" href="{form}">{copy["pricing"]} →</a>')
    band = (f'<section class="proofBand"><div><span>{copy["guides"]}</span><h2>{copy["guideHeading"]}</h2></div>'
            f'<p>{copy["guideIntro"]}</p><a href="{prefix}/guides">{copy["guideLink"]}</a></section>')
    text = replace_one(text, r'<section class="proofBand">.*?</section>', band)
    write_text(page, text)


def add_guides(out: Path, lang: str, copy: dict) -> set[str]:
    prefix = "/en" if lang == "en" else ""
    all_guides = []
    hashes = set()
    for slug in ("ai-safety-for-kids", "ai-first-tasks-for-adults", *NEW_GUIDES):
        guide = guides.parse_guide(ROOT / "guides" / "aiskillab" / f"{slug}.{lang}.md")
        if guide["slug"] != slug or guide["path"] != f"{prefix}/guides/{slug}" or guide["lang"] != lang:
            raise ValueError(f"Guide metadata mismatch for {slug}.{lang}")
        all_guides.append(guide)
        if slug not in NEW_GUIDES:
            continue
        key = "businessAction" if slug == "ai-pilot-for-small-business" else "adultAction"
        action = f'<p class="guideCrosslink"><a href="{prefix}/start#application-form">{copy[key]} →</a></p>'
        main = replace_one(guides.article_main(guide), "</article></main>", action + "</article></main>")
        article = guides.build_page(lang, title=guide["seo_title"], description=guide["description"],
                                    route=guide["path"], alternate=guide["alternate"], page_type="article",
                                    image_alt="AI Skill Lab · Phuket", main=main,
                                    schemas=guides.schemas_for(guide))
        page = out / (guide["path"].lstrip("/") + ".html")
        if page.exists():
            raise ValueError(f"Unexpected existing route {guide['path']}")
        write_text(page, article)
        for script in re.findall(r'<script type="application/ld\+json">(.*?)</script>', article, flags=re.S):
            encoded = base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
            hashes.add(f"'sha256-{encoded}'")
    listing = out / f'{prefix.lstrip("/") + "/" if prefix else ""}guides.html'
    text = listing.read_text(encoding="utf-8")
    all_guides.sort(key=lambda item: item["reviewed"], reverse=True)
    write_text(listing, replace_one(text, r'<main id="main" class="guideMain">.*?</main>', guides.listing_main(lang, all_guides)))
    return hashes


def extend_discovery(out: Path, hashes: set[str]) -> None:
    config_path = out / "vercel.json"
    config = json.loads(config_path.read_bytes())
    headers = next(rule["headers"] for rule in config["headers"] if rule["source"] == "/(.*)")
    csp = next(h for h in headers if h["key"] == "Content-Security-Policy")
    policy = csp["value"].split("; ")
    idx = next(i for i, rule in enumerate(policy) if rule.startswith("script-src "))
    policy[idx] += "".join(" " + item for item in sorted(hashes - set(policy[idx].split())))
    csp["value"] = "; ".join(policy)
    write_text(config_path, json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    sitemap_path = out / "sitemap.xml"
    sitemap = sitemap_path.read_text(encoding="utf-8")
    entries = []
    for slug in NEW_GUIDES:
        for prefix in ("", "/en"):
            url = f"{guides.ORIGIN}{prefix}/guides/{slug}"
            entries.append(f"<url><loc>{url}</loc><lastmod>2026-11-18</lastmod></url>")
    write_text(sitemap_path, replace_one(sitemap, "</urlset>", "\n".join(entries) + "\n</urlset>"))
    llms = out / "llms.txt"
    lines = [f"- [RU]({guides.ORIGIN}/guides/{s}) [EN]({guides.ORIGIN}/en/guides/{s})" for s in NEW_GUIDES]
    write_text(llms, replace_one(llms.read_text(encoding="utf-8"), r"## Guides\n", "## Guides\n" + "\n".join(lines) + "\n"))


def build(destination: Path) -> None:
    destination = destination.resolve()
    if destination.exists() or destination.is_relative_to(LIVE):
        raise ValueError("Use a new output directory outside deploy/live")
    raw = (LIVE / "_release.json").read_bytes()
    if digest(raw) != PARENT:
        raise ValueError("Review the new parent release before rebuilding this candidate")
    with TemporaryDirectory(dir=destination.parent) as staging:
        out = Path(staging) / "site"
        out.mkdir()
        for row in json.loads(raw)["files"]:
            rel = row["path"]
            data = (LIVE / rel).read_bytes()
            if digest(data) != row["sha256"] or len(data) != row["size"]:
                raise ValueError(f"Parent asset mismatch: {rel}")
            target = out / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        copy = json.loads((ROOT / "data/conversion-home-r1.json").read_bytes())
        hashes = set()
        for lang in ("ru", "en"):
            wording = {k: html.escape(v) for k, v in copy[lang].items()}
            build_home(out, lang, wording)
            hashes.update(add_guides(out, lang, wording))
        extend_discovery(out, hashes)
        files = []
        for path in sorted(out.rglob("*"), key=lambda p: p.relative_to(out).as_posix()):
            if path.is_file():
                data = path.read_bytes()
                files.append({"path": path.relative_to(out).as_posix(), "size": len(data), "sha256": digest(data)})
        aggregate = "".join(f"{item['path']}\t{item['size']}\t{item['sha256']}\n" for item in files).encode()
        manifest = {"schema": "ai-skill-lab.static-release.v1", "release_id": RELEASE, "parent_manifest_sha256": PARENT,
                    "payload_sha256": digest(aggregate), "file_count": len(files), "files": files}
        write_text(out / "_release.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        out.rename(destination)
        print(f"{RELEASE} files={len(files)} payload_sha256={manifest['payload_sha256']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    build(parser.parse_args().destination)
