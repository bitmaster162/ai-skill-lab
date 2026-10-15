#!/usr/bin/env python3
"""Exact read-only verifier for R3.1 sitemap freshness successor.

The 108-asset R3.1 manifest is an immutable parent; only sitemap.xml changes.
All contents are byte-compared against independently reconstructed output.
"""
from __future__ import annotations
import hashlib
import json
from collections.abc import Mapping

import build_site_r31_sitemap_r2 as build

ROOT = build.ROOT
LIVE = build.LIVE
PATCH = build.PATCH
RELEASE = build.RELEASE
EXPECTED_MANIFEST_SHA = build.EXPECTED_MANIFEST_SHA
EXPECTED_PAYLOAD_SHA = build.EXPECTED_PAYLOAD_SHA


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def active() -> bool:
    try:
        m = json.loads((LIVE / "_release.json").read_bytes())
        return m.get("release_id") == RELEASE and m.get("patch_id") == PATCH
    except (OSError, ValueError, TypeError):
        return False


def check_release(overrides: Mapping[str, bytes | None] | None = None) -> dict:
    generated, report = build.render()
    if report["manifest_sha256"] != EXPECTED_MANIFEST_SHA or report["payload_sha256"] != EXPECTED_PAYLOAD_SHA:
        raise ValueError("R31_SITEMAP_R2_HOLD pinned_regeneration")
    observed: dict[str, bytes] = {}
    for path in LIVE.rglob("*"):
        if path.is_symlink():
            raise ValueError("R31_SITEMAP_R2_HOLD unapproved_symlink")
        if path.is_file():
            observed[path.relative_to(LIVE).as_posix()] = path.read_bytes()
    for rel, raw in dict(overrides or {}).items():
        if (not isinstance(rel, str) or not rel or rel.startswith("/") or
                ".." in rel.split("/") or "\\" in rel):
            raise ValueError("R31_SITEMAP_R2_HOLD unapproved_fixture_path")
        if raw is None:
            observed.pop(rel, None)
        elif type(raw) is bytes:
            observed[rel] = raw
        else:
            raise ValueError("R31_SITEMAP_R2_HOLD nonbinary_fixture")
    if set(observed) != set(generated):
        raise ValueError("R31_SITEMAP_R2_HOLD asset_inventory_drift")
    changed = [name for name in generated if generated[name] != observed[name]]
    if changed:
        raise ValueError("R31_SITEMAP_R2_HOLD asset_byte_drift:" + ",".join(changed[:4]))
    raw_manifest = observed["_release.json"]
    if sha(raw_manifest) != EXPECTED_MANIFEST_SHA:
        raise ValueError("R31_SITEMAP_R2_HOLD manifest_byte_pin")
    manifest = json.loads(raw_manifest)
    if (manifest.get("schema"), manifest.get("release_id"), manifest.get("patch_id"),
            manifest.get("parent_manifest_sha256"), manifest.get("file_count"),
            manifest.get("payload_sha256")) != (
            "ai-skill-lab.static-release.v1", RELEASE, PATCH,
            build.PARENT_MANIFEST_SHA, 108, EXPECTED_PAYLOAD_SHA):
        raise ValueError("R31_SITEMAP_R2_HOLD signed_lineage_fields")
    recorded = {entry["path"]: {"size": entry["size"], "sha256": entry["sha256"]}
                for entry in manifest["files"]}
    if len(recorded) != 108 or recorded != {
        name: {"size": len(raw), "sha256": sha(raw)}
        for name, raw in observed.items() if name != "_release.json"
    }:
        raise ValueError("R31_SITEMAP_R2_HOLD manifest_record_mismatch")
    if observed["sitemap.xml"] != build.update_sitemap(build.git("show", build.BASE + ":deploy/live/sitemap.xml")):
        raise ValueError("R31_SITEMAP_R2_HOLD non_scoped_xml")
    for path, approved in (
        ("phuket-universe.html", "Условия размещения обсуждаем индивидуально — напишите нам."),
        ("en/phuket-universe.html", "Listing terms are discussed individually — write to us."),
    ):
        if observed[path].count(approved.encode("utf-8")) != 1 or b'id="agency-pilot-terms"' in observed[path]:
            raise ValueError("R31_SITEMAP_R2_HOLD r7c_approved_copy")
    if b"const ENABLED = false;" not in observed["phuket-universe-events.js"]:
        raise ValueError("R31_SITEMAP_R2_HOLD e38_not_dormant")
    return {
        "status": "LOCAL_PASS", "patch": PATCH, "base": build.BASE,
        "parent_manifest_sha256": build.PARENT_MANIFEST_SHA,
        "manifest_sha256": EXPECTED_MANIFEST_SHA, "payload_sha256": EXPECTED_PAYLOAD_SHA,
        "assets": 108, "routes": 56, "changed_static": ["sitemap.xml", "_release.json"],
        "normal_lastmod": build.NORMAL_DAY, "normal_routes": 54,
        "universe_lastmod": build.UNIVERSE_DAY, "universe_routes": 2,
        "production_authority": False, "universe_events_enabled": False,
    }


def inherited_pin_overrides() -> dict[str, str]:
    check_release()
    generated, _ = build.render()
    return {
        "deploy/live/sitemap.xml": sha(generated["sitemap.xml"]),
        "deploy/live/_release.json": sha(generated["_release.json"]),
        "app/sitemap.ts": sha(
            (ROOT / "app/sitemap.ts").read_bytes().replace(b"\r\n", b"\n")),
    }


if __name__ == "__main__":
    print(json.dumps(check_release(), ensure_ascii=False, sort_keys=True))
