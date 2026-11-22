"""Verify the two contextual pilot-guide links against the sealed #256 review tree."""
from functools import lru_cache
import json
import re
from urllib.parse import quote, unquote

import ru_guide_cards_release as cards
from guide_donor_release import git, sha
from restored_guides_release import manifest_bytes

ROOT, LIVE = cards.ROOT, cards.LIVE
PARENT_COMMIT = "ac3ef1398a62c2819e40a3291cbe4a82f5ee2078"
SOURCE_COMMIT = "ca680f9197b7bb7ff9a4809d96a3bab0fdfe56b6"
RELEASE_ID = "AISL_BUSINESS_PILOT_LINKS_R2_20261122"
MANIFEST_SHA = "f0d308a383d92bd5ab21e13e77b09d8461e87b39749789d4db65e504e9df50ed"
PAYLOAD_SHA = "da4c30eb94eef0c360cd63aaa87f954600c58e5420dc04d8b8fad5f2b3d1f00c"
COMPONENT = "components/workshop/WorkshopBusiness.tsx"
COMPONENT_SHA = "92cb07fa0c645eaec0930df4954618cf7f1c5be97312ce8294570ffe2b8108ab"
LINKS = {
    "business.html": ("/guides/ai-pilot-for-small-business", "Как выбрать первую задачу для ИИ-пилота"),
    "en/business.html": ("/en/guides/ai-pilot-for-small-business", "How to choose the first task for an AI pilot"),
}
CHANGED = set(LINKS)


def require(condition, reason):
    if not condition:
        raise ValueError("BUSINESS_PILOT_LINKS_DENY: " + reason)


def active():
    manifest = LIVE / "_release.json"
    return not LIVE.is_symlink() and manifest.is_file() and not manifest.is_symlink() and sha(manifest.read_bytes()) == MANIFEST_SHA


def source_sha(rel):
    if rel != COMPONENT:
        return cards.source_sha(rel)
    path = ROOT / rel
    require(path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == COMPONENT_SHA, "component")
    return COMPONENT_SHA


def compact_intro_url(original):
    # Keep ASCII (including reserved escape sequences) exactly as approved; URL
    # serialization will UTF-8 percent-encode the Cyrillic letters on navigation.
    result = re.sub(r"%(?:D0|D1)%[0-9A-F]{2}", lambda match: unquote(match[0]), original)
    require(quote(result, safe=":/?=%") == original, "intro URL serialization")
    return result


def expected_contact_url(rel, original):
    if rel == "business.html" and original.startswith("https://wa.me/66649701204?text=") and active():
        return compact_intro_url(original)
    return original


@lru_cache(maxsize=1)
def expected_files():
    """Reconstruct from immutable Git ancestors, never cache readings of the working release."""
    for commit in (PARENT_COMMIT, SOURCE_COMMIT):
        git("merge-base", "--is-ancestor", commit, "HEAD")
    source = git("show", SOURCE_COMMIT + ":" + COMPONENT)
    require(sha(source) == COMPONENT_SHA, "reviewed source")
    expected = dict(cards.expected_files())
    parent = expected["_release.json"]
    require(sha(parent) == cards.MANIFEST_SHA and parent == git("show", PARENT_COMMIT + ":deploy/live/_release.json"), "parent manifest")
    manifest = json.loads(parent)
    rows = {row["path"]: row for row in manifest["files"]}
    require(len(rows) == len(manifest["files"]) == manifest["file_count"] == 116, "inventory")
    marker = b'</section><section class="section panelSection" id="pilot-simulator">'
    for rel, (url, label) in LINKS.items():
        page = expected[rel]
        require(page.count(marker) == 1 and page.split(marker)[0].endswith(b'</article></div>'), "pilot section " + rel)
        require(label.encode() in source and url.encode() not in page, "pilot link " + rel)
        addition = f'<div class="heroActions"><a class="workshopButton workshopButtonSecondary" href="{url}">{label}</a></div>'.encode()
        expected[rel] = page.replace(marker, addition + marker)
        if rel == "business.html":
            match, = re.findall(rb'href="(https://wa[.]me/66649701204[?]text=[^"]+)"', page)
            expected[rel] = expected[rel].replace(match, compact_intro_url(match.decode("ascii")).encode())
        rows[rel].update(size=len(expected[rel]), sha256=sha(expected[rel]))
    listing = "".join(f"{r['path']}\t{r['size']}\t{r['sha256']}\n" for r in manifest["files"])
    require(sha(listing.encode()) == PAYLOAD_SHA, "payload")
    manifest.update(release_id=RELEASE_ID, patch_id=RELEASE_ID, parent_manifest_sha256=cards.MANIFEST_SHA,
                    payload_sha256=PAYLOAD_SHA)
    expected["_release.json"] = manifest_bytes(manifest)
    require(sha(expected["_release.json"]) == MANIFEST_SHA, "manifest")
    return expected


def verify():
    # Retain every historical source check that the two-card release uses.
    inherited = (set(cards.sitemap_route_dates_release.SOURCE_SHA) | cards.certificate_donor_release.SOURCE_CHANGES
                 | set(cards.telegram_card_release.SOURCE_SHA) | set(cards.universe_en_home_release.SOURCE_SHA)
                 | set(cards.previous.SOURCE_SHA) | set(cards.SOURCE_SHA) | {COMPONENT})
    for rel in sorted(inherited):
        source_sha(rel)
    for script in ("restored_guides_release", "test_restored_guides_release", "ru_guide_cards_release", "test_ru_guide_cards_release"):
        rel = "scripts/" + script + ".py"
        path = ROOT / rel
        require(path.is_file() and not path.is_symlink() and path.read_bytes() == git("show", PARENT_COMMIT + ":" + rel), "historical verifier " + rel)
    expected = expected_files()
    require(LIVE.is_dir() and not LIVE.is_symlink(), "release root")
    entries = list(LIVE.rglob("*"))
    require(all(not p.is_symlink() and (p.is_file() or p.is_dir()) for p in entries), "filesystem entry")
    require({p.relative_to(LIVE).as_posix() for p in entries if p.is_file()} == expected.keys(), "unexpected or missing asset")
    for rel, contents in expected.items():
        require((LIVE / rel).read_bytes() == contents, "static " + rel)
    return json.loads(expected["_release.json"])


def static_main_sha(rel):
    verify()
    parts = re.findall(rb'<main id="main".*?</main>', (LIVE / rel).read_bytes(), re.S)
    require(len(parts) == 1, "main " + rel)
    return sha(parts[0])

