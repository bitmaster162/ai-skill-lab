#!/usr/bin/env python3
"""Independent fail-closed read-only validation of R3.1 post-R7C local candidate."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from collections.abc import Mapping
import build_site_r31_post_r7c as candidate

ROOT = candidate.ROOT
LIVE = candidate.LIVE
PATCH = candidate.PATCH
RELEASE = candidate.RELEASE
BASE = candidate.BASE
BASE_TREE = candidate.BASE_TREE
EXPECTED_MANIFEST_SHA = candidate.EXPECTED_MANIFEST_SHA
EXPECTED_PAYLOAD_SHA = candidate.EXPECTED_PAYLOAD_SHA
ALLOWED_MODIFIED = candidate.ALLOWED_MODIFIED


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def active() -> bool:
    try:
        m = json.loads((LIVE / "_release.json").read_bytes())
        import site_r31_sitemap_r2_profile as sitemap_r2
        return (m.get("release_id") == RELEASE and
                m.get("patch_id") in {PATCH, sitemap_r2.PATCH})
    except (OSError, ValueError, TypeError):
        return False


def is_sitemap_r2() -> bool:
    import site_r31_sitemap_r2_profile as sitemap_r2
    return sitemap_r2.active()


def expected_manifest_sha() -> str:
    import site_r31_sitemap_r2_profile as sitemap_r2
    return sitemap_r2.EXPECTED_MANIFEST_SHA if sitemap_r2.active() else EXPECTED_MANIFEST_SHA


def check_release(overrides: Mapping[str, bytes | None] | None = None) -> dict:
    if is_sitemap_r2():
        from site_r31_sitemap_r2_profile import check_release as check_sitemap
        return check_sitemap(overrides)
    generated, expected = candidate.render()
    if expected["manifest_sha256"] != EXPECTED_MANIFEST_SHA or expected["payload_sha256"] != EXPECTED_PAYLOAD_SHA:
        raise ValueError("R31_PORT_HOLD expected_digest_drift")
    overrides = dict(overrides or {})
    observed: dict[str, bytes] = {}
    for path in LIVE.rglob("*"):
        if path.is_symlink():
            raise ValueError("R31_PORT_HOLD symlink")
        if path.is_file():
            rel = path.relative_to(LIVE).as_posix()
            observed[rel] = path.read_bytes()
    for rel, data in overrides.items():
        if not isinstance(rel, str) or not rel or rel.startswith("/") or "\\" in rel or ".." in rel.split("/"):
            raise ValueError("R31_PORT_HOLD unsafe_fixture_path")
        if data is None:
            observed.pop(rel, None)
        elif type(data) is bytes:
            observed[rel] = data
        else:
            raise ValueError("R31_PORT_HOLD nonbytes_fixture")
    if set(observed) != set(generated):
        raise ValueError("R31_PORT_HOLD inventory_mismatch")
    different = [k for k in generated if observed[k] != generated[k]]
    if different:
        raise ValueError("R31_PORT_HOLD byte_mismatch:" + ",".join(different[:4]))
    raw = observed["_release.json"]
    if sha(raw) != EXPECTED_MANIFEST_SHA:
        raise ValueError("R31_PORT_HOLD manifest_sha")
    m = json.loads(raw)
    if (m.get("release_id"), m.get("patch_id"), m.get("parent_manifest_sha256"),
            m.get("file_count"), m.get("payload_sha256")) != (
            RELEASE, PATCH, candidate.PARENT_MANIFEST_SHA, 108, EXPECTED_PAYLOAD_SHA):
        raise ValueError("R31_PORT_HOLD manifest_lineage")
    ru = observed["start.html"]
    en = observed["en/start.html"]
    for lang, page in (("ru", ru), ("en", en)):
        note, direct = candidate.NOTE[lang]
        if not (page.count(b'data-lead-state="unready"') == 1
                and page.count(b'data-lead-readiness') == 1
                and page.count(b'data-lead-direct-contact') == 1
                and page.count(b'type="submit" disabled') == 1
                and page.count(b'src="/lead-form-runtime.js"') == 1
                and page.count(note.encode()) == 1
                and page.count(direct.encode()) == 1):
            raise ValueError("R31_PORT_HOLD form_fail_closed:" + lang)
    if b"const ENABLED = false;" not in observed["phuket-universe-events.js"]:
        raise ValueError("R31_PORT_HOLD e38_authority")
    if b'id="agency-pilot-terms"' in observed["phuket-universe.html"]:
        raise ValueError("R31_PORT_HOLD r7c_reversion")
    if not (observed["sitemap.xml"] == candidate.git("show", BASE + ":deploy/live/sitemap.xml")
            and observed["lead-form-runtime.js"] == (ROOT / "public/lead-form-runtime.js").read_bytes()):
        raise ValueError("R31_PORT_HOLD route_dates_or_runtime_parity")
    return {
        "status": "LOCAL_PASS", "base": BASE, "patch": PATCH,
        "assets": 108, "routes": 56, "modified": sorted(ALLOWED_MODIFIED),
        "added": ["lead-form-runtime.js"], "manifest_sha256": EXPECTED_MANIFEST_SHA,
        "payload_sha256": EXPECTED_PAYLOAD_SHA, "production_authority": False,
        "universe_events_enabled": False,
    }


def legacy_r6_html_for_parity(rel: str) -> bytes:
    """Only after pinned R3.1-R7C verification, reconstruct immutable R6 text."""
    import phuket_universe_r7b_release_profile as r7b
    import build_phuket_universe_r7
    p = r7b.profile()
    if rel not in p["changed_r6_files"] or not rel.endswith(".html"):
        raise ValueError("R31_PORT_HOLD unreviewed_legacy_route")
    old = r7b.git_blob("3d58999a382b2c11eae7da3d97e9e650c1326f46",
                      "deploy/live/" + rel)
    old_pin = p["r6_file_pins"][rel]
    if len(old) != old_pin["size"] or sha(old) != old_pin["sha256"]:
        raise ValueError("R31_PORT_HOLD historic_r6_hash")
    r7 = r7b.git_blob(r7b.PREV_HEAD, "deploy/live/" + rel)
    r7_pin = p["r7_html_pins"][rel]
    if len(r7) != r7_pin["size"] or sha(r7) != r7_pin["sha256"]:
        raise ValueError("R31_PORT_HOLD historic_r7_hash")
    if build_phuket_universe_r7.make_page(rel, old.decode("utf-8")).encode("utf-8") != r7:
        raise ValueError("R31_PORT_HOLD r6_to_r7_replay")
    # The caller has already verified the full exact manifest and candidate replay.
    manifest = json.loads((LIVE / "_release.json").read_bytes())
    if sha((LIVE / "_release.json").read_bytes()) != expected_manifest_sha():
        raise ValueError("R31_PORT_HOLD parity_manifest_drift")
    entries = {entry["path"]: entry for entry in manifest["files"]}
    pin = entries.get(rel)
    current = (LIVE / rel).read_bytes()
    if not pin or pin["size"] != len(current) or pin["sha256"] != sha(current):
        raise ValueError("R31_PORT_HOLD current_page_drift")
    return old


def inherited_pin_overrides() -> dict[str, str]:
    """All SHA-256 values derive from the independently pinned exact candidate."""
    check_release()
    files, _ = candidate.render()
    changed = ALLOWED_MODIFIED | {"_release.json", "lead-form-runtime.js"}
    result = {"deploy/live/" + rel: sha(files[rel]) for rel in changed}
    for rel in ("phuket-universe.html", "en/phuket-universe.html"):
        result["deploy/live/" + rel] = sha(files[rel])
    if is_sitemap_r2():
        from site_r31_sitemap_r2_profile import inherited_pin_overrides as add_sitemap_pins
        result.update(add_sitemap_pins())
    return result


if __name__ == "__main__":
    print(json.dumps(check_release(), sort_keys=True))
