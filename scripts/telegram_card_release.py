"""Verify the two direct Telegram labels and their dated sitemap against release #249."""
from functools import lru_cache
import json
import re

import certificate_donor_release as previous
from guide_donor_release import git, sha

ROOT, LIVE = previous.ROOT, previous.LIVE
PARENT_COMMIT = "b1f079a5d435d4c0e487df1905268ea5eb28024a"
PARENT_SHA = previous.MANIFEST_SHA
RELEASE_ID = "AISL_TELEGRAM_CARD_R1_20261122"
DATE = "2026-11-22"
MANIFEST_SHA = "e70b076b1f754bc3dac1b402c70362d773d61e9ba2a4fbe7f7dc12c56bfd28f2"
PAYLOAD_SHA = "bd07783abfa0c8313d334ef33dd5449f09c2544385fedf72c0323455994b9d1c"
LABELS = {
    "start.html": ("Короткое описание задачи с автозаполнением", "Написать в Telegram"),
    "en/start.html": ("Brief with prefill", "Message on Telegram"),
}
CHANGED = {*LABELS, "sitemap.xml"}
SOURCE_SHA = {
    "components/workshop/ChannelLinks.tsx": "522ad2972aff14aa83b1c074a82ce141d74685c8ec55712f612d0abd588e522c",
    "app/sitemap.ts": "129d9eb04efa931aae5decf0a2a15f942d381c68dd99f455ad87e7886dcfe8a1",
    "lib/guides.ts": "2479b369ebf17a63b841edf41faf18d64be86b90be98b7254d4c4a653a1d21b4",
}


def require(condition, reason):
    if not condition:
        raise ValueError("TELEGRAM_CARD_DENY " + reason)


@lru_cache(maxsize=None)
def original(path):
    return git("show", f"{PARENT_COMMIT}:{path}")


def expected_static(path):
    data = original("deploy/live/" + path)
    if path == "sitemap.xml":
        for route in ("/start", "/en/start"):
            entry = f"<loc>https://aiskillab.work{route}</loc><lastmod>2026-11-21</lastmod>"
            data = previous.replace_once(data, entry, entry.replace("2026-11-21", DATE))
        return data
    old, new = LABELS[path]
    return previous.replace_once(data, f"<span>Telegram</span><strong>{old}</strong>",
                                 f"<span>Telegram</span><strong>{new}</strong>")


def active():
    path = LIVE / "_release.json"
    return path.is_file() and sha(path.read_bytes()) == MANIFEST_SHA


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
    for path in ("scripts/certificate_donor_release.py", "scripts/test_certificate_donor_release.py"):
        require((ROOT / path).read_bytes() == original(path), "historical verifier " + path)

    static = dict(file_overrides or {})
    updated = {}
    for path in sorted(CHANGED):
        data = static.get(path, (LIVE / path).read_bytes())
        require(not (LIVE / path).is_symlink() and data == expected_static(path), "static " + path)
        updated[path] = {"path": path, "size": len(data), "sha256": sha(data)}
        static[path] = original("deploy/live/" + path)
    sources = dict(source_overrides or {})
    for path, digest in SOURCE_SHA.items():
        data = sources.pop(path, (ROOT / path).read_bytes())
        require(not (ROOT / path).is_symlink() and sha(data) == digest, "source " + path)
        if path in previous.SOURCE_CHANGES:
            sources[path] = original(path)

    # Replay the preceding release on its original versions of all superseded inputs.
    parent = previous.verify(manifest_override=original("deploy/live/_release.json"),
                             file_overrides=static, source_overrides=sources)
    manifest = json.loads(raw)
    require(manifest["patch_id"] == manifest["release_id"] == RELEASE_ID and
            manifest["parent_manifest_sha256"] == PARENT_SHA, "parent identity")
    rows = [updated.get(row["path"], row) for row in parent["files"]]
    require(manifest["files"] == rows and manifest["file_count"] == len(rows) == 112, "inventory")
    listing = "".join(f"{r['path']}\t{r['size']}\t{r['sha256']}\n" for r in rows)
    require(manifest["payload_sha256"] == sha(listing.encode()) == PAYLOAD_SHA, "payload")
    return manifest


def static_main_sha(rel):
    verify()
    matches = re.findall(rb'<main id="main".*?</main>', (LIVE / rel).read_bytes(), re.S)
    require(len(matches) == 1, "main " + rel)
    return sha(matches[0])
