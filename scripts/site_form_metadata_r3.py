"""Exact local release profile. Passing validation never authorizes a deployment.

The historical T1.6F2 validator remains unchanged except for its explicit CLI
successor dispatch. Unknown IDs and changed manifests/payloads fail closed.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
RELEASE = "SITE_FORM_METADATA_R3_20261014"
PARENT = "T1_6F2_ADULT_FIRST_TASKS_R1"
PAYLOAD_SHA = "ae8e2affc11c6d946b08a14c2d90b1a312b3efdf16334234998bcc087c090a57"
PINS_SHA = "bbc7780dada7127b26ed24acad245f7966d008552e4ad29ddbfc75bdcbcba890"
PINS_PATH = "data/site_form_metadata_r3_pins.json"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def strict_json(raw: bytes):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError("duplicate JSON key: " + key)
            out[key] = value
        return out
    return json.loads(raw, object_pairs_hook=unique)


def canonical_source(raw: bytes) -> bytes:
    lf = raw.replace(b"\r\n", b"\n")
    if b"\r" in lf or raw.count(b"\r\n") not in (0, raw.count(b"\n")):
        raise ValueError("mixed or noncanonical source line endings")
    return lf


def load_pins(root: Path = ROOT) -> dict:
    raw = (root / PINS_PATH).read_bytes()
    if sha(raw) != PINS_SHA:
        raise ValueError("release pin record SHA mismatch")
    pins = strict_json(raw)
    if pins.get("release_id") != RELEASE or pins.get("payload_sha256") != PAYLOAD_SHA:
        raise ValueError("release pin identity mismatch")
    return pins


def is_current(root: Path = ROOT) -> bool:
    return strict_json((root / "deploy/live/_release.json").read_bytes()).get("release_id") == RELEASE


def validate(root: Path = ROOT, overrides: Mapping[str, bytes | None] | None = None,
             include_sources: bool = True) -> dict:
    """Read-only verification; overrides are exclusively in-memory negative fixtures."""
    root = root.resolve()
    supplied = dict(overrides or {})
    errors = []
    checks = 0
    def need(ok, reason):
        nonlocal checks
        checks += 1
        if not ok:
            errors.append(reason)
    def read(rel):
        if rel in supplied:
            raw = supplied[rel]
            if not isinstance(raw, bytes):
                raise ValueError("missing/nonbyte fixture: " + rel)
            return raw
        path = root / rel
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError("unsafe path: " + rel)
        return path.read_bytes()
    try:
        pins = load_pins(root)
        raw = read("deploy/live/_release.json")
        need(sha(raw) == pins["manifest_sha256"], "exact manifest SHA")
        manifest = strict_json(raw)
        need(type(manifest) is dict, "manifest is an object")
        if type(manifest) is not dict:
            raise ValueError("manifest not an object")
        need(manifest.get("release_id") == RELEASE, "exact release ID")
        need(manifest.get("schema") == "ai-skill-lab.static-release.v1", "manifest schema")
        need(type(manifest.get("file_count")) is int and manifest["file_count"] == 99, "99 files")
        need(manifest.get("payload_sha256") == PAYLOAD_SHA, "exact payload field")
        need(raw == (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(), "canonical manifest")
        need(manifest.get("files") == pins["files"], "exact independent inventory")
        actual = {p.relative_to(root / "deploy/live").as_posix()
                  for p in (root / "deploy/live").rglob("*") if p.is_file() and p != root / "deploy/live/_release.json"}
        for name, data in supplied.items():
            if name.startswith("deploy/live/") and name != "deploy/live/_release.json":
                rel = name.removeprefix("deploy/live/")
                if data is None:
                    actual.discard(rel)
                else:
                    actual.add(rel)
        expected = {f["path"] for f in pins["files"]}
        need(actual == expected, "physical inventory has no missing or extra files")
        records = []
        for f in pins["files"]:
            name = f["path"]
            need(not name.startswith("/") and ".." not in name.split("/") and "\\" not in name, "safe asset path")
            data = read("deploy/live/" + name)
            item = {"path": name, "size": len(data), "sha256": sha(data)}
            records.append(item)
            need(item == f, "exact asset: " + name)
        aggregate = "".join(f"{f['path']}\t{f['size']}\t{f['sha256']}\n" for f in records).encode()
        need(sha(aggregate) == PAYLOAD_SHA, "recomputed exact payload")
        need(sum(f["size"] for f in records) <= 1200 * 1024, "unchanged total byte budget")
        need(sum(f["size"] for f in records if not f["path"].endswith(".woff2")) <= 1120 * 1024, "unchanged nonfont byte budget")
        if include_sources:
            for name, digest in pins["source_sha256_lf"].items():
                need(sha(canonical_source(read(name))) == digest, "exact source: " + name)
        need(read("public/lead-form-runtime.js") == read("deploy/live/lead-form-runtime.js"), "source and shipped runtime parity")
    except (OSError, ValueError, TypeError, KeyError, UnicodeError) as exc:
        need(False, str(exc))
    return {"release": RELEASE, "checks": checks, "errors": errors, "release_authorization": False}


def require_current(root: Path = ROOT) -> None:
    result = validate(root)
    if result["errors"]:
        raise ValueError("SITE_R3_SEAL_FAIL: " + "; ".join(result["errors"][:8]))


def cli() -> int:
    result = validate()
    print(json.dumps(result, sort_keys=True))
    print("SITE_R3_SEAL_PASS" if not result["errors"] else "SITE_R3_SEAL_FAIL")
    return 1 if result["errors"] else 0
