"""Verify the one-asset matcher successor to the four restored guides."""
from functools import lru_cache
import json
import re

import certificate_donor_release
import restored_guides_release as previous
import sitemap_route_dates_release
import telegram_card_release
import universe_en_home_release
from guide_donor_release import sha, git

ROOT, LIVE = previous.ROOT, previous.LIVE
PARENT_COMMIT = "2444bd77f7616ba916c37b2b3bcba11898926be0"
PARENT_SHA = previous.MANIFEST_SHA
RELEASE_ID = "AISL_MATCHER_FALLBACK_BRIEF_R1_20261122"
MANIFEST_SHA = "d4de99d99f7542afb5e853fecfbcc85674ac6dcd07d5c10d3c72154e20268329"
PAYLOAD_SHA = "78156621b653912264fc2a540f6f455c17b3b4a76be384ee744948805ec04615"
CHANGED = {"matcher-v2.js"}
GUIDE_SOURCE_SHA = "761cbac4c851477e6eb84e3119835eb6b399bb9a591f4a012e7679b2762bf9ae"


def require(ok, message):
    if not ok:
        raise ValueError("MATCHER_BRIEF_DENY: " + message)


@lru_cache(maxsize=None)
def original(path):
    return git("show", f"{PARENT_COMMIT}:{path}")


def active():
    path = LIVE / "_release.json"
    return path.is_file() and sha(path.read_bytes()) == MANIFEST_SHA


def source_sha(rel):
    if rel != "lib/guides.ts":
        return previous.source_sha(rel)
    path = ROOT / rel
    require(not path.is_symlink() and sha(path.read_bytes()) == GUIDE_SOURCE_SHA, "source " + rel)
    return GUIDE_SOURCE_SHA


def successor(matcher):
    raw = original("deploy/live/_release.json")
    require(sha(raw) == PARENT_SHA, "parent manifest")
    parent = json.loads(raw)
    rows = parent["files"]
    row, = (item for item in rows if item["path"] == "matcher-v2.js")
    row.update(size=len(matcher), sha256=sha(matcher))
    listing = "".join(f"{r['path']}\t{r['size']}\t{r['sha256']}\n" for r in rows)
    return dict(parent, release_id=RELEASE_ID, patch_id=RELEASE_ID, parent_manifest_sha256=PARENT_SHA,
                payload_sha256=sha(listing.encode()))


def verify():
    raw = (LIVE / "_release.json").read_bytes()
    require(sha(raw) == MANIFEST_SHA, "manifest digest")
    git("merge-base", "--is-ancestor", PARENT_COMMIT, "HEAD")
    inherited_sources = (set(sitemap_route_dates_release.SOURCE_SHA)
                         | certificate_donor_release.SOURCE_CHANGES
                         | set(telegram_card_release.SOURCE_SHA)
                         | set(universe_en_home_release.SOURCE_SHA) | set(previous.SOURCE_SHA))
    for rel in sorted(inherited_sources):
        source_sha(rel)
    for rel in ("scripts/restored_guides_release.py", "scripts/test_restored_guides_release.py"):
        require((ROOT / rel).read_bytes() == original(rel), "historical verifier " + rel)
    manifest = successor((LIVE / "matcher-v2.js").read_bytes())
    require(raw == previous.manifest_bytes(manifest) and manifest["payload_sha256"] == PAYLOAD_SHA,
            "successor reconstruction")
    paths = list(LIVE.rglob("*"))
    require(all(not p.is_symlink() for p in paths), "symlink in release")
    files = {p.relative_to(LIVE).as_posix() for p in paths if p.is_file()}
    require(files == {r["path"] for r in manifest["files"]} | {"_release.json"}, "asset inventory")
    for row in manifest["files"]:
        path = LIVE / row["path"]
        require(path.stat().st_size == row["size"] and sha(path.read_bytes()) == row["sha256"],
                "static " + row["path"])
    return manifest


def static_main_sha(rel):
    verify()
    parts = re.findall(rb'<main id="main".*?</main>', (LIVE / rel).read_bytes(), re.S)
    require(len(parts) == 1, "main " + rel)
    return sha(parts[0])
