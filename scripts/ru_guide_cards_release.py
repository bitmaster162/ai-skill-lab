"""Verify the exact two-card successor of the 116-asset restored-guide release."""
from functools import lru_cache
import json
import re

import certificate_donor_release
import restored_guides_release as previous
import sitemap_route_dates_release
import stage_first_tasks_card as stage
import telegram_card_release
import universe_en_home_release
from guide_donor_release import git, sha

ROOT, LIVE = previous.ROOT, previous.LIVE
PARENT_COMMIT = "2444bd77f7616ba916c37b2b3bcba11898926be0"
PARENT_SHA = "66c02d9bda23b0424330596b6e74a14576be0259d31f4e1b5a5f8ba07cb251d5"
RELEASE_ID = "AISL_RU_GUIDE_CARDS_R1_20261122"
MANIFEST_SHA = "3cf9c37a1487444c73d8631bbc39c2c4b48b5101d321f37fb3fbb65e37fea25a"
PAYLOAD_SHA = "097e44a211afe7b7b37be8544bc1ec798dc414ed5f63400733d3cf7c4cad9bbc"
CHANGED = {"guides/ai-first-tasks-for-adults.html", "guides/ai-pilot-for-small-business.html"}
SOURCE_SHA = {
    "app/(ru)/guides/[slug]/page.tsx": "1c65e83c130a471c93d10babea20e3464083df88983fd0a20ab297bb31af8a28",
    "guides/aiskillab/social-cards.json": "8943cb13104c397775b71d27ba8daabce9e6aec12673a5c998ae9dc67cb00491",
    "scripts/build_guides.py": "55ec6fc4349813cb75a76499974886f823b2b74e7d63874797d3212fe8a2012a",
    "scripts/stage_first_tasks_card.py": "231df3e3b755cff399e4d770c8524ad98c84e6da55463f52867a879f0bc8745f",
    "lib/guides.ts": "57eefeeab6f78334ddf4e3119adcb2402dbaa9f258f983b4772889c625884516",
}


def require(condition, reason):
    if not condition:
        raise ValueError("RU_GUIDE_CARDS_DENY: " + reason)


@lru_cache(maxsize=None)
def original(rel):
    return git("show", f"{PARENT_COMMIT}:{rel}")


def active():
    manifest = LIVE / "_release.json"
    return not LIVE.is_symlink() and not manifest.is_symlink() and manifest.is_file() and sha(manifest.read_bytes()) == MANIFEST_SHA


def source_sha(rel):
    path = ROOT / rel
    require(path.is_file() and not path.is_symlink(), "source " + rel)
    if rel not in SOURCE_SHA:
        return previous.source_sha(rel)
    require(sha(path.read_bytes()) == SOURCE_SHA[rel], "source " + rel)
    return SOURCE_SHA[rel]


def reviewed_cards():
    """Return the pinned two-route card map only on this exact manifest."""
    if not active():
        return {}
    rel = "guides/aiskillab/social-cards.json"
    source_sha(rel)
    return json.loads((ROOT / rel).read_bytes())


@lru_cache(maxsize=1)
def expected_files():
    """Cache only the reconstruction from sealed Git inputs; verify live inputs on every call."""
    git("merge-base", "--is-ancestor", PARENT_COMMIT, "HEAD")
    parent_raw = original("deploy/live/_release.json")
    require(sha(parent_raw) == PARENT_SHA, "parent manifest")
    parent_rows = {r["path"]: r for r in json.loads(parent_raw)["files"]}
    files = stage.candidate("restored", include_pilot=True)
    raw = files["_release.json"]
    require(sha(raw) == MANIFEST_SHA, "reconstructed manifest")
    manifest = json.loads(raw)
    require(manifest["patch_id"] == manifest["release_id"] == RELEASE_ID
            and manifest["parent_manifest_sha256"] == PARENT_SHA
            and manifest["payload_sha256"] == PAYLOAD_SHA, "release identity")
    rows = {r["path"]: r for r in manifest["files"]}
    require(len(rows) == len(manifest["files"]) == manifest["file_count"] == 116
            and rows.keys() == parent_rows.keys()
            and files.keys() == rows.keys() | {"_release.json"}, "reconstructed inventory")
    require({p for p in rows if rows[p] != parent_rows[p]} == CHANGED, "two-page delta")
    return files


def verify():
    inherited = (set(sitemap_route_dates_release.SOURCE_SHA) | certificate_donor_release.SOURCE_CHANGES
                 | set(telegram_card_release.SOURCE_SHA) | set(universe_en_home_release.SOURCE_SHA)
                 | set(previous.SOURCE_SHA))
    for rel in sorted(inherited | SOURCE_SHA.keys()):
        source_sha(rel)
    for rel in ("scripts/restored_guides_release.py", "scripts/test_restored_guides_release.py"):
        path = ROOT / rel
        require(path.is_file() and not path.is_symlink() and path.read_bytes() == original(rel),
                "historical verifier " + rel)
    expected = expected_files()
    require(LIVE.is_dir() and not LIVE.is_symlink(), "release root")
    entries = list(LIVE.rglob("*"))
    require(all(not p.is_symlink() and (p.is_file() or p.is_dir()) for p in entries),
            "unexpected filesystem entry")
    actual = {p.relative_to(LIVE).as_posix() for p in entries if p.is_file()}
    require(actual == expected.keys(), "unexpected or missing asset")
    for rel, content in expected.items():
        require((LIVE / rel).read_bytes() == content, "static " + rel)
    return json.loads(expected["_release.json"])


def static_main_sha(rel):
    verify()
    parts = re.findall(rb'<main id="main".*?</main>', (LIVE / rel).read_bytes(), re.S)
    require(len(parts) == 1, "main " + rel)
    return sha(parts[0])
