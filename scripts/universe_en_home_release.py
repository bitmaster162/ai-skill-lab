"""Verify the English Phuket Universe home link and its route date against release #250."""
from functools import lru_cache
import json
import re

import telegram_card_release as previous
from certificate_donor_release import replace_once
from guide_donor_release import git, sha

ROOT, LIVE = previous.ROOT, previous.LIVE
PARENT_COMMIT = "d21bed353d696f453e605a34a3382112715f22d8"
PARENT_SHA = previous.MANIFEST_SHA
RELEASE_ID = "AISL_UNIVERSE_EN_HOME_R1_20261122"
DATE = "2026-11-22"
MANIFEST_SHA = "ba386c11a929a0a668e5d7d0be72dd272e93fcf924e11d7cd505c2354c9e4c5a"
PAYLOAD_SHA = "4e2f844016e35b5b60b371ad3839cc284ee65be921bb976bca88b815b1c5fd24"
CHANGED = {
    "en/phuket-universe.html": ('rel="noopener" href="https://aiskillab.work">AI Skill Lab',
                                'rel="noopener" href="/en">AI Skill Lab'),
    "sitemap.xml": ("/en/phuket-universe</loc><lastmod>2026-10-15",
                    f"/en/phuket-universe</loc><lastmod>{DATE}"),
}
SOURCE_SHA = {
    "app/sitemap.ts": "ed2638be28dd1b6707d1402ab1494f60c440e5953e0cc3b11aff1ce5e606a5a8",
    "components/phuketUniverseMarkup.ts": "014dea264d3b5b30fdcc006bebf828be35487572703f5c3f4ddbab11236e0ad9",
    "lib/guides.ts": "5b75e851e846c4ef16002104d7a25740cc02c27f947659964ee92d088ee3156d",
    "scripts/prepare_phuket_universe_u1.py": "68d8bb5be6bfd35bd8fa107ac7374f983142a4c5b770c165827b6c8aeb722fab",
}


def require(condition, message):
    if not condition:
        raise ValueError("UNIVERSE_EN_HOME_DENY " + message)


@lru_cache(maxsize=None)
def original(path):
    return git("show", f"{PARENT_COMMIT}:{path}")


def active():
    manifest = LIVE / "_release.json"
    return manifest.is_file() and sha(manifest.read_bytes()) == MANIFEST_SHA


def source_sha(rel):
    if rel not in SOURCE_SHA:
        return previous.source_sha(rel)
    digest = sha((ROOT / rel).read_bytes())
    require(digest == SOURCE_SHA[rel], "source " + rel)
    return digest


def verify(*, manifest_override=None, file_overrides=None, source_overrides=None):
    raw = (LIVE / "_release.json").read_bytes() if manifest_override is None else manifest_override
    require(sha(raw) == MANIFEST_SHA, "manifest digest")
    git("merge-base", "--is-ancestor", PARENT_COMMIT, "HEAD")
    for path in ("scripts/telegram_card_release.py", "scripts/test_telegram_card_release.py"):
        require((ROOT / path).read_bytes() == original(path), "historical verifier " + path)

    files = dict(file_overrides or {})
    rows = {}
    for path, (before, after) in CHANGED.items():
        parent_bytes = original("deploy/live/" + path)
        content = files.get(path, (LIVE / path).read_bytes())
        require(not (LIVE / path).is_symlink() and content == replace_once(parent_bytes, before, after),
                "static " + path)
        rows[path] = {"path": path, "size": len(content), "sha256": sha(content)}
        files[path] = parent_bytes

    sources = dict(source_overrides or {})
    for path, digest in SOURCE_SHA.items():
        content = sources.pop(path, (ROOT / path).read_bytes())
        require(not (ROOT / path).is_symlink() and sha(content) == digest, "source " + path)
        if path in previous.SOURCE_SHA:
            sources[path] = original(path)

    parent = previous.verify(manifest_override=original("deploy/live/_release.json"),
                             file_overrides=files, source_overrides=sources)
    manifest = json.loads(raw)
    require(manifest["patch_id"] == manifest["release_id"] == RELEASE_ID and
            manifest["parent_manifest_sha256"] == PARENT_SHA, "release identity")
    expected = [rows.get(row["path"], row) for row in parent["files"]]
    require(manifest["files"] == expected and manifest["file_count"] == len(expected) == 112, "inventory")
    listing = "".join(f"{r['path']}\t{r['size']}\t{r['sha256']}\n" for r in expected)
    require(manifest["payload_sha256"] == sha(listing.encode()) == PAYLOAD_SHA, "payload")
    return manifest


def static_main_sha(rel):
    verify()
    parts = re.findall(rb'<main id="main".*?</main>', (LIVE / rel).read_bytes(), re.S)
    require(len(parts) == 1, "main " + rel)
    return sha(parts[0])
