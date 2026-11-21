"""Admit only the two localized completion-record links and their sitemap dates."""
from functools import lru_cache
import json
import re

import sitemap_route_dates_release as previous
from guide_donor_release import git, sha

ROOT, LIVE = previous.ROOT, previous.LIVE
RELEASE_ID = "AISL_CERTIFICATE_DONORS_R1_20261122"
PARENT_COMMIT = "880009028f22d89da7a70d4867c8f9509f87e9ff"
PARENT_SHA = previous.MANIFEST_SHA
MANIFEST_SHA = "a1906e1cd855e9fa54fe20de10c3769f2df650cf3efb1c6d3e1ce987b7a3a4c6"
PAYLOAD_SHA = "3e00d5460f488ae3a80f5c754601c7f27d544400b8700411c6e6ae4feb356755"
DATE = "2026-11-22"
# The production static pages and the Next pages use different layouts.
# Each insertion follows the existing privacy statement in its own layout.
LINKS = {
    "safety.html": (
        "app/(ru)/safety/page.tsx", "/certificate",
        "Как оформляется запись о завершении проекта",
        "Мы не требуем публичной публикации детских проектов или личной информации.",
        "Перед загрузкой фото, файлов или школьных материалов отдельно оцениваем, нужны ли они вообще.",
    ),
    "en/safety.html": (
        "app/(en)/en/safety/page.tsx", "/en/certificate",
        "How project completion is recorded",
        "We do not require public posting of youth projects or personal information.",
        "Photos, files and school materials are used only when genuinely needed.",
    ),
}
CHANGED = set(LINKS) | {"sitemap.xml"}
SOURCE_CHANGES = {"lib/guides.ts", "app/sitemap.ts", *(row[0] for row in LINKS.values())}


def require(condition, reason):
    if not condition:
        raise ValueError("CERTIFICATE_DONORS_DENY " + reason)


@lru_cache(maxsize=None)
def original(rel):
    return git("show", f"{PARENT_COMMIT}:{rel}")


def replace_once(data, old, new):
    before = old.encode()
    require(data.count(before) == 1, "unique insertion point: " + old)
    return data.replace(before, new.encode(), 1)


def amended(rel):
    data = original(rel)
    if rel == "lib/guides.ts":
        marker = '    ]);\n    const seal = typeof header.release_id'
        addition = (f'      ["{RELEASE_ID}", {{\n'
                    f'        count: 112,\n        parent: "{PARENT_SHA}",\n'
                    f'        payload: "{PAYLOAD_SHA}",\n        manifest: "{MANIFEST_SHA}",\n'
                    '      }],\n')
        return replace_once(data, marker, addition + marker)
    if rel == "app/sitemap.ts":
        old = 'if (route === "/safety" || route === "/en/safety") return "2026-10-29";'
        return replace_once(data, old, old.replace("2026-10-29", DATE))
    if rel == "deploy/live/sitemap.xml":
        for page in LINKS:
            entry = "<loc>https://aiskillab.work/" + page.removesuffix(".html") + "</loc><lastmod>2026-10-29</lastmod>"
            data = replace_once(data, entry, entry.replace("2026-10-29", DATE))
        return data
    for page, (source, href, label, static_text, source_text) in LINKS.items():
        if rel == "deploy/live/" + page:
            return replace_once(data, static_text + "</li>", f'{static_text} <a href="{href}">{label}</a>.</li>')
        if rel == source:
            return replace_once(data, source_text + "</p>", f'{source_text} <Link href="{href}">{label}</Link>.</p>')
    raise ValueError("Unknown certificate-donor release path: " + rel)


def active():
    path = LIVE / "_release.json"
    return path.is_file() and sha(path.read_bytes()) == MANIFEST_SHA


def source_sha(rel):
    if rel not in SOURCE_CHANGES:
        return previous.source_sha(rel)
    data = (ROOT / rel).read_bytes()
    require(data == amended(rel), "source " + rel)
    return sha(data)


def verify(*, manifest_override=None, file_overrides=None, source_overrides=None):
    raw = (LIVE / "_release.json").read_bytes() if manifest_override is None else manifest_override
    require(sha(raw) == MANIFEST_SHA, "manifest digest")
    git("merge-base", "--is-ancestor", PARENT_COMMIT, "HEAD")
    for rel in ("scripts/sitemap_route_dates_release.py", "scripts/test_sitemap_route_dates_release.py"):
        require((ROOT / rel).read_bytes() == original(rel), "historical verifier " + rel)
    manifest = json.loads(raw)
    require(manifest["release_id"] == manifest["patch_id"] == RELEASE_ID and
            manifest["parent_manifest_sha256"] == PARENT_SHA, "manifest identity")

    files = dict(file_overrides or {})
    sources = dict(source_overrides or {})
    new_rows = {}
    for page in sorted(CHANGED):
        rel = "deploy/live/" + page
        data = files.get(page, (ROOT / rel).read_bytes())
        require(not (ROOT / rel).is_symlink() and data == amended(rel), "static " + page)
        new_rows[page] = {"path": page, "size": len(data), "sha256": sha(data)}
        files[page] = original(rel)
    for rel in SOURCE_CHANGES:
        data = sources.pop(rel, (ROOT / rel).read_bytes())
        require(data == amended(rel), "source " + rel)
    for rel in ("app/sitemap.ts", "lib/guides.ts"):
        sources[rel] = original(rel)
    parent = previous.verify(manifest_override=original("deploy/live/_release.json"),
                             file_overrides=files, source_overrides=sources)
    rows = [new_rows.get(row["path"], row) for row in parent["files"]]
    require(manifest["files"] == rows and manifest["file_count"] == parent["file_count"] == 112,
            "three changed assets")
    listing = "".join(f"{r['path']}\t{r['size']}\t{r['sha256']}\n" for r in rows)
    require(manifest["payload_sha256"] == PAYLOAD_SHA == sha(listing.encode()), "payload")
    return manifest


def static_main_sha(rel):
    verify()
    main = re.findall(rb'<main id="main".*?</main>', (LIVE / rel).read_bytes(), re.S)
    require(len(main) == 1, "main " + rel)
    return sha(main[0])
