#!/usr/bin/env python3
"""Exact site R3 payload, deterministic rebuild and in-memory rejection fixtures.

No network, publication, production writes or modification of historical pins.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
from unittest.mock import patch
import site_form_metadata_r3 as profile

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    raw = (ROOT / "deploy/live/_release.json").read_bytes()
    manifest = profile.strict_json(raw)
    release = manifest.get("release_id")
    if release in (profile.PARENT, "E3_6_WORKSHOP_HERO_PANEL_R1"):
        print("SITE_R3_NOT_APPLICABLE release=" + release)
        return 0
    if release != profile.RELEASE:
        raise ValueError("unknown release cannot use site R3 admission")
    positive = profile.validate(ROOT)
    if positive["errors"]:
        raise ValueError("positive seal failed: " + repr(positive["errors"]))
    pins = profile.load_pins(ROOT)
    fixtures = {"deploy/live/" + f["path"]: (ROOT / "deploy/live" / f["path"]).read_bytes() for f in pins["files"]}
    fixtures.update({name: (ROOT / name).read_bytes() for name in pins["source_sha256_lf"]})
    fixtures["deploy/live/_release.json"] = raw
    negative = 0
    kinds: dict[str, int] = {}

    def reject(kind: str, edits: dict[str, bytes | None]) -> None:
        nonlocal negative
        result = profile.validate(ROOT, {**fixtures, **edits})
        if not result["errors"] or result["release_authorization"] is not False:
            raise ValueError("negative fixture accepted: " + kind)
        negative += 1
        kinds[kind.split(":", 1)[0]] = kinds.get(kind.split(":", 1)[0], 0) + 1

    for f in pins["files"]:
        name = "deploy/live/" + f["path"]
        reject("asset_changed:" + f["path"], {name: fixtures[name] + b"\nR3_MUTATION"})
        reject("asset_missing:" + f["path"], {name: None})
    for name in pins["source_sha256_lf"]:
        reject("source_changed:" + name, {name: fixtures[name] + b"\nR3_MUTATION"})
        reject("source_missing:" + name, {name: None})
    for name in ("extra.html", "nested/_release.json", "../outside.txt"):
        reject("unexpected_asset:" + name, {"deploy/live/" + name: b"synthetic"})
    for key, value in (("release_id", "UNKNOWN"), ("release_id", profile.PARENT), ("file_count", True),
                       ("file_count", 98), ("schema", "unknown"), ("payload_sha256", "0" * 64)):
        altered = dict(manifest)
        altered[key] = value
        reject("manifest_field:" + key, {"deploy/live/_release.json": (json.dumps(altered, sort_keys=True, indent=2) + "\n").encode()})
    reject("malformed_manifest", {"deploy/live/_release.json": b"{"})
    reject("duplicate_manifest_key", {"deploy/live/_release.json": b'{"release_id":"X","release_id":"Y"}'})
    reject("noncanonical_manifest", {"deploy/live/_release.json": json.dumps(manifest).encode()})
    reject("manifest_missing", {"deploy/live/_release.json": None})
    # Even a self-consistently rehashed altered manifest cannot replace reviewed pins.
    forged = json.loads(raw)
    forged["files"][0]["sha256"] = "0" * 64
    forged["payload_sha256"] = profile.sha("".join(f"{f['path']}\t{f['size']}\t{f['sha256']}\n" for f in forged["files"]).encode())
    reject("recomputed_manifest_forgery", {"deploy/live/_release.json": (json.dumps(forged, sort_keys=True, indent=2) + "\n").encode()})
    try:
        profile.strict_json(b'{"a":1,"a":2}')
    except ValueError:
        negative += 1
        kinds["strict_duplicate_key"] = 1
    else:
        raise ValueError("duplicate JSON parser accepted duplicate key")
    # Checkout LF/CRLF differences are allowed; mixed endings are not.
    source_name = "components/LeadForm.tsx"
    lf = profile.canonical_source(fixtures[source_name])
    portable = profile.validate(ROOT, {**fixtures, source_name: lf.replace(b"\n", b"\r\n")})
    if portable["errors"]:
        raise ValueError("uniform CRLF was incorrectly rejected")
    reject("mixed_source_endings", {source_name: lf.replace(b"\n", b"\r\n", 1)})
    # Same release identity does not admit arbitrary guide routes or altered guides.
    import guide_route_admission as routes
    expected = routes.BASELINE_ROUTES | {"/guides/ai-first-tasks-for-adults", "/en/guides/ai-first-tasks-for-adults"}
    if routes.admitted_routes() != expected:
        raise ValueError("R3 retained guide pair is not exactly admitted")
    real_read = Path.read_bytes
    real_text = Path.read_text
    for damaged in ("deploy/live/_release.json", "guides/aiskillab/ai-first-tasks-for-adults.en.md", "deploy/live/en/guides/ai-first-tasks-for-adults.html"):
        target = ROOT / damaged
        def modified_bytes(path):
            return b"{}" if path == target else real_read(path)
        def modified_text(path, *args, **kwargs):
            return "{}" if path == target else real_text(path, *args, **kwargs)
        with patch.object(Path, "read_bytes", modified_bytes), patch.object(Path, "read_text", modified_text):
            if routes.admitted_routes() != routes.BASELINE_ROUTES:
                raise ValueError("guide admitted despite corrupt evidence: " + damaged)
        negative += 1
        kinds["guide_evidence_changed"] = kinds.get("guide_evidence_changed", 0) + 1
    from build_site_release_r3 import render
    rebuilt = render()
    actual = {p.relative_to(ROOT / "deploy/live").as_posix(): p.read_bytes() for p in (ROOT / "deploy/live").rglob("*") if p.is_file()}
    if rebuilt != actual:
        raise ValueError("deterministic rebuild differs from candidate")
    print(json.dumps({"release": release, "positive_checks": positive["checks"], "negative_fixtures": negative,
                      "fixture_kinds": kinds, "rebuild_files": len(actual), "uniform_crlf": "PASS",
                      "guide_routes": len(expected), "publication_authorization": False}, sort_keys=True))
    print("SITE_R3_INTEGRITY_AND_NEGATIVES_PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print("SITE_R3_FAIL " + str(exc))
        sys.exit(1)
