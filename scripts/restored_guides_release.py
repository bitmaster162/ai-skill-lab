"""Reproduce and verify the four previously published guide routes on the #251 runtime.

The prior conversion release shipped both slugs in Actions artifact 14422506762
(run 44293573770, source #238). #240 archived the corresponding static root.
This successor rebuilds only the reviewed articles and their discovery metadata.
"""
from functools import lru_cache
import base64
import hashlib
import json
import re

import build_guides as renderer
import certificate_donor_release
import sitemap_route_dates_release
import telegram_card_release
import universe_en_home_release as previous
from guide_donor_release import git, sha

ROOT, LIVE = previous.ROOT, previous.LIVE
PARENT_COMMIT = "3cfec05da23fd1556636753f3d0773651c3072eb"
PARENT_SHA = previous.MANIFEST_SHA
RELEASE_ID = "AISL_RESTORED_GUIDES_R1_20261122"
DATE = "2026-11-22"
ORIGIN = renderer.ORIGIN
SLUGS = ("ai-pilot-for-small-business", "ai-start-for-adults")
LANGS = ("ru", "en")
NEW_ROUTES = {f"{prefix}/guides/{slug}" for prefix in ("", "/en") for slug in SLUGS}
ADDITIONS = {route[1:] + ".html" for route in NEW_ROUTES}
CHANGED = ADDITIONS | {"guides.html", "en/guides.html", "sitemap.xml", "llms.txt", "vercel.json"}
MANIFEST_SHA = "66c02d9bda23b0424330596b6e74a14576be0259d31f4e1b5a5f8ba07cb251d5"
PAYLOAD_SHA = "f11a64758e9c5661eea55a24b9a98c6c078e17dcdfca8e335bd04c23776d99e5"
SOURCE_SHA = {
    "README.md": "7dfff9761911106b2babfd01c0e331a45055f491fcd1423dcac2858fa1a8bf33",
    "components/guides/GuidePages.tsx": "dcd057d215f3fd52497bd8fa19c3e5a5bd203a96c580e9a96b8f1fb584d47c33",
    "app/sitemap.ts": "ea3c6b4b2c817a3e0751d3595c237ba782a6f9d607e80ab928225e875bf8d9be",
    "guides/aiskillab/ai-pilot-for-small-business.en.md": "a2da0faf2c0a92d693672d2c956aafdf14fad3772f0d05751603d200796d4115",
    "guides/aiskillab/ai-pilot-for-small-business.ru.md": "cf7e4c696d27a21116097938af013200daacb6d886c0eb91da0c1da95b07b111",
    "guides/aiskillab/ai-start-for-adults.en.md": "87e15c28a5642277a840cc3848c9588acd5db5a2370f9a94fb12acd203855623",
    "guides/aiskillab/ai-start-for-adults.ru.md": "9ef353f732c8527222918022dd80f0452d585997d120e25db848a9b7f89f5fc5",
    "lib/guides.ts": "bd1fe8b498ae08c10aca39934b9857de18b2cf1dd9c3723e9a39a863bb3ab8fa",
}
CTA = {
    "ai-pilot-for-small-business": {"ru": "Обсудить пилот для бизнеса", "en": "Discuss a business pilot"},
    "ai-start-for-adults": {"ru": "Обсудить индивидуальное обучение", "en": "Ask about one-to-one lessons"},
}


def require(condition, reason):
    if not condition:
        raise ValueError("RESTORED_GUIDES_DENY: " + reason)


@lru_cache(maxsize=None)
def original(path):
    return git("show", f"{PARENT_COMMIT}:{path}")


def active():
    path = LIVE / "_release.json"
    return path.is_file() and sha(path.read_bytes()) == MANIFEST_SHA


def source_sha(rel):
    if rel not in SOURCE_SHA:
        return previous.source_sha(rel)
    path = ROOT / rel
    require(not path.is_symlink() and sha(path.read_bytes()) == SOURCE_SHA[rel], "source " + rel)
    return SOURCE_SHA[rel]


def replace_once(text, before, after):
    require(text.count(before) == 1, "unique boundary " + before[:80])
    return text.replace(before, after, 1)


def article(guide):
    locale, slug = guide["lang"], guide["slug"]
    prefix = "/en" if locale == "en" else ""
    contact = f'<p class="guideCrosslink"><a href="{prefix}/start#application-form">{CTA[slug][locale]} →</a></p>'
    main = replace_once(renderer.article_main(guide), "</article></main>", contact + "</article></main>")
    return renderer.build_page(locale, title=guide["seo_title"], description=guide["description"],
                               route=guide["path"], alternate=guide["alternate"], page_type="article",
                               image_alt="AI Skill Lab · Phuket", main=main, schemas=renderer.schemas_for(guide))


def static_delta():
    delta = {}
    script_hashes = set()
    for lang in LANGS:
        prefix = "en/" if lang == "en" else ""
        all_guides = []
        for slug in ("ai-safety-for-kids", "ai-first-tasks-for-adults", *SLUGS):
            guide = renderer.parse_guide(ROOT / "guides/aiskillab" / f"{slug}.{lang}.md")
            all_guides.append(guide)
            if slug not in SLUGS:
                continue
            route = "/" + prefix + "guides/" + slug
            require(guide["path"] == route and guide["lang"] == lang, "localized article source")
            content = article(guide)
            delta[route[1:] + ".html"] = content.encode()
            for script in re.findall(r'<script type="application/ld\+json">(.*?)</script>', content, re.S):
                digest = base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
                script_hashes.add(f"'sha256-{digest}'")
        listing = prefix + "guides.html"
        catalog = original("deploy/live/" + listing).decode()
        pattern = r'<main id="main" class="guideMain">.*?</main>'
        listings = re.findall(pattern, catalog, re.S)
        require(len(listings) == 1, "guide catalog " + listing)
        all_guides.sort(key=lambda item: item["reviewed"], reverse=True)
        delta[listing] = replace_once(catalog, listings[0], renderer.listing_main(lang, all_guides)).encode()

    sitemap = original("deploy/live/sitemap.xml").decode()
    for catalog in ("/guides", "/en/guides"):
        pattern = rf"(<loc>{re.escape(ORIGIN + catalog)}</loc><lastmod>)([\d-]+)(</lastmod>)"
        sitemap, count = re.subn(pattern, lambda m: m[1] + DATE + m[3], sitemap)
        require(count == 1, "sitemap catalog " + catalog)
    entries = "".join(f"<url><loc>{ORIGIN}{r}</loc><lastmod>{DATE}</lastmod></url>" for r in sorted(NEW_ROUTES))
    delta["sitemap.xml"] = replace_once(sitemap, "</urlset>", entries + "</urlset>").encode()
    llms = original("deploy/live/llms.txt").decode()
    extra = "".join(f"- [RU]({ORIGIN}/guides/{s}) [EN]({ORIGIN}/en/guides/{s})\n" for s in SLUGS)
    marker = f"- [RU]({ORIGIN}/guides) [EN]({ORIGIN}/en/guides)\n"
    delta["llms.txt"] = replace_once(llms, marker, marker + extra).encode()
    config = json.loads(original("deploy/live/vercel.json"))
    root = next(rule for rule in config["headers"] if rule["source"] == "/(.*)")
    header = next(h for h in root["headers"] if h["key"] == "Content-Security-Policy")
    directives = header["value"].split("; ")
    for i, directive in enumerate(directives):
        if directive.startswith("script-src "):
            additions = sorted(script_hashes.difference(directive.split()))
            directives[i] = " ".join([directive, *additions])
    header["value"] = "; ".join(directives)
    delta["vercel.json"] = (json.dumps(config, indent=2, ensure_ascii=False) + "\n").encode()
    require(set(delta) == CHANGED, "candidate delta")
    return delta


def successor(delta):
    parent_raw = original("deploy/live/_release.json")
    require(sha(parent_raw) == PARENT_SHA, "parent manifest")
    parent = json.loads(parent_raw)
    rows = {item["path"]: item for item in parent["files"]}
    require(set(delta) - set(rows) == ADDITIONS and len(rows) == 112, "new route inventory")
    for name, data in delta.items():
        rows[name] = {"path": name, "size": len(data), "sha256": sha(data)}
    records = [rows[k] for k in sorted(rows)]
    listing = "".join(f"{r['path']}\t{r['size']}\t{r['sha256']}\n" for r in records)
    return dict(parent, release_id=RELEASE_ID, patch_id=RELEASE_ID, parent_manifest_sha256=PARENT_SHA,
                files=records, file_count=len(records), payload_sha256=sha(listing.encode()))


def manifest_bytes(manifest):
    return (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()


def verify():
    raw = (LIVE / "_release.json").read_bytes()
    require(sha(raw) == MANIFEST_SHA, "manifest digest")
    git("merge-base", "--is-ancestor", PARENT_COMMIT, "HEAD")
    # The November release gates protect additional Next and runtime sources beyond this change.
    inherited_sources = (set(sitemap_route_dates_release.SOURCE_SHA) | certificate_donor_release.SOURCE_CHANGES
                         | set(telegram_card_release.SOURCE_SHA) | set(previous.SOURCE_SHA))
    for rel in inherited_sources | set(SOURCE_SHA):
        source_sha(rel)
    for rel in ("scripts/universe_en_home_release.py", "scripts/test_universe_en_home_release.py"):
        require((ROOT / rel).read_bytes() == original(rel), "historical verifier " + rel)
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for route in sorted(NEW_ROUTES):
        readme = replace_once(readme, f"`{route}`, ", "")
    require(readme.encode() == original("README.md"), "guide inventory README preimage")
    manifest = successor(static_delta())
    require(raw == manifest_bytes(manifest) and manifest["payload_sha256"] == PAYLOAD_SHA and
            manifest["file_count"] == 116, "manifest reconstruction")
    paths = list(LIVE.rglob("*"))
    require(all(not path.is_symlink() for path in paths), "symlink in release")
    actual = {path.relative_to(LIVE).as_posix() for path in paths if path.is_file()}
    require(actual == {r["path"] for r in manifest["files"]} | {"_release.json"}, "unexpected or missing asset")
    for row in manifest["files"]:
        path = LIVE / row["path"]
        require(not path.is_symlink() and path.stat().st_size == row["size"] and
                sha(path.read_bytes()) == row["sha256"], "static " + row["path"])
    return manifest


def static_main_sha(rel):
    verify()
    parts = re.findall(rb'<main id="main".*?</main>', (LIVE / rel).read_bytes(), re.S)
    require(len(parts) == 1, "main " + rel)
    return sha(parts[0])
