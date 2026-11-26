"""Deterministic, fail-closed, in-memory versioned release admission.

Public validate_full() accepts ONLY immutable historical policy pins. It does not
publish anything. An internal _validate_under_test_trust() exists solely for
synthetic, pre-approved fixture tests and MUST NOT be used for production gates.
No network, subprocess, writes, environment variables, or dynamic imports.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
from html.parser import HTMLParser
from xml.etree import ElementTree as ET
import json
import re
from typing import Mapping, Sequence
from .baseline import BASELINE_ROUTES, route_digest
from .authority import APPROVED_HISTORICAL_PINS, BASELINE_ROUTE_SHA256

PROFILE_SCHEMA = "ai-skill-lab.release-profile.v1"
MANIFEST_SCHEMA = "ai-skill-lab.static-release.v1"
ORIGIN = "https://aiskillab.work"
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
_ID = re.compile(r"[A-Z0-9_]{4,96}\Z")
PROFILE_FIELDS = frozenset({
    "schema", "release_id", "mode", "origin", "baseline_route_set_sha256",
    "route_count", "file_count", "html_count", "guide_slugs",
    "manifest_sha256", "payload_sha256", "expected_payload_bytes",
    "expected_nonfont_bytes", "max_payload_bytes", "max_nonfont_bytes",
    "source_pins", "asset_pins",
})


class AdmissionDenied(ValueError):
    """Failed closed: never interpreted as positive publish permission."""
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class ProfileIdentity:
    release_id: str
    mode: str
    profile_sha256: str
    file_count: int
    route_count: int
    status: str = "IDENTITY_ONLY"
    live_bytes_verified: bool = False
    publication_authorized: bool = False


@dataclass(frozen=True)
class ValidationReceipt:
    release_id: str
    profile_sha256: str
    manifest_sha256: str
    payload_sha256: str
    asset_count: int
    route_count: int
    html_count: int
    guide_pairs: int
    status: str = "PASS_PROVIDED_BYTES"
    publication_authorized: bool = False


def _need(ok: bool, code: str) -> None:
    if not ok:
        raise AdmissionDenied(code)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _json_object_unique(pairs: list[tuple[str, object]]) -> dict:
    obj: dict = {}
    for key, val in pairs:
        _need(key not in obj, "DUPLICATE_JSON_KEY")
        obj[key] = val
    return obj


def _reject_constant(value: str):
    raise AdmissionDenied("INVALID_JSON_CONSTANT")


def _parse_json(raw: bytes, code: str) -> dict:
    _need(type(raw) is bytes, "INPUT_NOT_BYTES")
    try:
        result = json.loads(
            raw.decode("utf-8"), object_pairs_hook=_json_object_unique,
            parse_constant=_reject_constant,
        )
    except AdmissionDenied:
        raise
    except (UnicodeError, ValueError, TypeError) as error:
        raise AdmissionDenied(code) from error
    _need(type(result) is dict, "ROOT_NOT_OBJECT")
    return result


def _canonical_json(data: dict) -> bytes:
    return (json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def _is_hash(value: object) -> bool:
    return type(value) is str and bool(_HEX64.fullmatch(value))


def _safe_path(s: object) -> bool:
    if type(s) is not str or not s or len(s) > 512:
        return False
    if s.startswith("/") or "\\" in s or "\x00" in s or ":" in s:
        return False
    if any(ord(c) < 32 or ord(c) == 127 for c in s):
        return False
    return all(part not in ("", ".", "..") for part in s.split("/"))


def _positive_int(value: object) -> bool:
    return type(value) is int and value > 0


def _nonnegative_int(value: object) -> bool:
    return type(value) is int and value >= 0


def accepted_routes(guide_slugs: Sequence[str]) -> frozenset[str]:
    """52 exact T1.5 baseline routes plus each explicitly admitted bilingual pair."""
    routes = set(BASELINE_ROUTES)
    _need(type(guide_slugs) in (list, tuple), "SLUGS_NOT_SEQUENCE")
    _need(all(type(x) is str for x in guide_slugs), "INVALID_GUIDE_SLUG")
    _need(len(guide_slugs) == len(set(guide_slugs)), "DUPLICATE_GUIDE_SLUG")
    for slug in guide_slugs:
        _need(bool(_SLUG.fullmatch(slug)), "INVALID_GUIDE_SLUG")
        ru, en = "/guides/" + slug, "/en/guides/" + slug
        _need(ru not in routes and en not in routes, "BASELINE_ROUTE_COLLISION")
        routes.update((ru, en))
    return frozenset(routes)


def _check_profile(profile: dict, declared_release_id: str, *, allow_synthetic: bool) -> None:
    _need(set(profile) == PROFILE_FIELDS, "PROFILE_SCHEMA_FIELDS")
    _need(profile["schema"] == PROFILE_SCHEMA, "PROFILE_SCHEMA_VERSION")
    _need(type(declared_release_id) is str and bool(_ID.fullmatch(declared_release_id)), "INVALID_RELEASE_ID")
    _need(profile["release_id"] == declared_release_id, "RELEASE_ID_MISMATCH")
    _need(profile["mode"] in (("historical", "synthetic") if allow_synthetic else ("historical",)), "PROFILE_MODE_DENIED")
    _need(profile["origin"] == ORIGIN, "UNAPPROVED_ORIGIN")
    _need(route_digest(BASELINE_ROUTES) == BASELINE_ROUTE_SHA256, "BASELINE_ROUTE_DRIFT")
    _need(profile["baseline_route_set_sha256"] == BASELINE_ROUTE_SHA256, "PROFILE_BASELINE_DRIFT")
    for key in ("manifest_sha256", "payload_sha256"):
        _need(_is_hash(profile[key]), "INVALID_PROFILE_HASH")
    for key in ("file_count", "route_count", "html_count", "expected_payload_bytes", "expected_nonfont_bytes", "max_payload_bytes", "max_nonfont_bytes"):
        _need(_positive_int(profile[key]), "INVALID_PROFILE_INT_" + key)
    _need(type(profile["guide_slugs"]) is list, "GUIDE_LIST_TYPE")
    slugs = profile["guide_slugs"]
    _need(slugs == sorted(slugs) if all(type(x) is str for x in slugs) else False, "GUIDES_NOT_SORTED")
    routes = accepted_routes(slugs)
    _need(profile["route_count"] == len(routes), "PROFILE_ROUTE_COUNT")
    _need(profile["html_count"] == len(routes) + 1, "PROFILE_HTML_COUNT")
    _need(profile["expected_payload_bytes"] <= profile["max_payload_bytes"], "PROFILE_PAYLOAD_OVER_BUDGET")
    _need(profile["expected_nonfont_bytes"] <= profile["max_nonfont_bytes"], "PROFILE_NONFONT_OVER_BUDGET")
    _need(profile["expected_nonfont_bytes"] <= profile["expected_payload_bytes"], "PROFILE_NONFONT_GT_TOTAL")
    pins = profile["asset_pins"]
    sources = profile["source_pins"]
    _need(type(pins) is dict and type(sources) is dict, "PINS_NOT_OBJECT")
    for path, pin in pins.items():
        _need(_safe_path(path), "INVALID_PINNED_ASSET_PATH")
        _need(type(pin) is dict and set(pin) == {"size", "sha256"}, "PIN_ASSET_FIELDS")
        _need(_nonnegative_int(pin["size"]) and _is_hash(pin["sha256"]), "PIN_ASSET_TYPE")
    for path, digest in sources.items():
        _need(_safe_path(path) and _is_hash(digest), "PIN_SOURCE_TYPE")
    for slug in slugs:
        for language in ("ru", "en"):
            source = f"guides/aiskillab/{slug}.{language}.md"
            asset = f"{'en/' if language == 'en' else ''}guides/{slug}.html"
            _need(source in sources and asset in pins, "GUIDE_PAIR_PINS_MISSING")


def _approved_profile(declared_id: str, profile_bytes: bytes, trusted_pins: Mapping[str, str], *, test_mode: bool) -> tuple[dict, str]:
    _need(type(declared_id) is str and declared_id in trusted_pins, "UNKNOWN_RELEASE_DENIED")
    _need(type(profile_bytes) is bytes, "PROFILE_NOT_BYTES")
    actual = _sha(profile_bytes)
    _need(actual == trusted_pins[declared_id], "PROFILE_NOT_IN_INDEPENDENT_TRUST_ROOT")
    profile = _parse_json(profile_bytes, "PROFILE_INVALID_JSON")
    _need(profile_bytes == _canonical_json(profile), "PROFILE_NONCANONICAL")
    _check_profile(profile, declared_id, allow_synthetic=test_mode)
    return profile, actual


def verify_profile_identity(release_id: str, profile_bytes: bytes) -> ProfileIdentity:
    """Historical profile identity only. NEVER a proof of live artifact bytes."""
    profile, digest = _approved_profile(release_id, profile_bytes, APPROVED_HISTORICAL_PINS, test_mode=False)
    return ProfileIdentity(release_id, profile["mode"], digest, profile["file_count"], profile["route_count"])


def _manifest_structure(blob: bytes) -> dict:
    data = _parse_json(blob, "MANIFEST_INVALID_JSON")
    _need(list(data) == ["file_count", "files", "payload_sha256", "release_id", "schema"], "MANIFEST_CANONICAL_FIELDS")
    _need(blob == _canonical_json(data), "MANIFEST_NONCANONICAL")
    _need(data["schema"] == MANIFEST_SCHEMA, "MANIFEST_SCHEMA")
    _need(_positive_int(data["file_count"]) and type(data["files"]) is list, "MANIFEST_COUNT_OR_RECORDS_TYPE")
    _need(_is_hash(data["payload_sha256"]), "MANIFEST_PAYLOAD_HASH_FORMAT")
    items = data["files"]
    _need(len(items) == data["file_count"], "MANIFEST_RECORD_COUNT")
    paths = []
    for record in items:
        _need(type(record) is dict and list(record) == ["path", "sha256", "size"], "MANIFEST_RECORD_FIELDS")
        path = record["path"]
        _need(_safe_path(path), "MANIFEST_UNSAFE_PATH")
        _need(path != "_release.json", "MANIFEST_SELF_REFERENCE")
        _need(_nonnegative_int(record["size"]) and _is_hash(record["sha256"]), "MANIFEST_RECORD_PIN_FORMAT")
        paths.append(path)
    _need(len(paths) == len(set(paths)), "MANIFEST_DUPLICATE_PATH")
    _need(paths == sorted(paths), "MANIFEST_UNSORTED_PATHS")
    return data


class _GuideHtmlProbe(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lang_values: list[str] = []
        self.canonicals: list[str] = []
        self.alternates: dict[str, list[str]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html":
            self.lang_values.append(values.get("lang") or "")
        if tag == "link" and values.get("rel") == "canonical":
            self.canonicals.append(values.get("href") or "")
        if tag == "link" and values.get("rel") == "alternate" and values.get("hreflang"):
            self.alternates.setdefault(values["hreflang"] or "", []).append(values.get("href") or "")


def _check_guides(profile: dict, assets: Mapping[str, bytes]) -> None:
    for slug in profile["guide_slugs"]:
        ru = ORIGIN + "/guides/" + slug
        en = ORIGIN + "/en/guides/" + slug
        for locale in ("ru", "en"):
            path = ("en/" if locale == "en" else "") + "guides/" + slug + ".html"
            raw = assets[path]
            try:
                probe = _GuideHtmlProbe()
                probe.feed(raw.decode("utf-8"))
            except (UnicodeError, ValueError) as err:
                raise AdmissionDenied("GUIDE_HTML_INVALID_UTF8") from err
            _need(probe.lang_values == [locale], "GUIDE_HTML_LOCALE")
            _need(probe.canonicals == [ru if locale == "ru" else en], "GUIDE_HTML_CANONICAL")
            _need(probe.alternates == {"ru": [ru], "en": [en], "x-default": [ru]}, "GUIDE_HTML_HREFLANG")


def _route_for_asset(path: str) -> str:
    if path == "index.html":
        return "/"
    if path == "en.html":
        return "/en"
    return "/" + path[:-5]


def _exact_urls(urls: Sequence[str], expected: frozenset[str], reason: str) -> None:
    _need(type(urls) in (list, tuple), reason + "_TYPE")
    _need(all(type(u) is str for u in urls), reason + "_NONSTRING")
    _need(len(urls) == len(set(urls)), reason + "_DUPLICATE")
    _need(set(urls) == expected, reason + "_SET")


def _validate_under_test_trust(
    release_id: str, profile_bytes: bytes, manifest_bytes: bytes,
    assets: Mapping[str, bytes], sources: Mapping[str, bytes],
    public_routes: Sequence[str], sitemap_urls: Sequence[str], llms_urls: Sequence[str],
    trusted_pins: Mapping[str, str], *, test_mode: bool,
) -> ValidationReceipt:
    """Pure engine. Only the outer production wrapper supplies real authority.

    The `test_mode` / `trusted_pins` injection is for sandbox tests only.
    It must never be used as production or owner approval.
    """
    profile, profile_sha = _approved_profile(release_id, profile_bytes, trusted_pins, test_mode=test_mode)
    _need(type(manifest_bytes) is bytes, "MANIFEST_NOT_BYTES")
    manifest_sha = _sha(manifest_bytes)
    _need(manifest_sha == profile["manifest_sha256"], "MANIFEST_SHA_NOT_APPROVED")
    manifest = _manifest_structure(manifest_bytes)
    _need(manifest["release_id"] == release_id, "MANIFEST_RELEASE_ID")
    _need(manifest["file_count"] == profile["file_count"], "MANIFEST_PROFILE_COUNT")
    _need(manifest["payload_sha256"] == profile["payload_sha256"], "MANIFEST_PAYLOAD_NOT_APPROVED")
    _need(type(assets) is dict and type(sources) is dict, "BUNDLE_NOT_MAPPING")
    by_path = {row["path"]: row for row in manifest["files"]}
    _need(set(assets) == set(by_path), "PHYSICAL_ASSET_INVENTORY")
    _need(set(sources) == set(profile["source_pins"]), "SOURCE_INVENTORY")
    for path, raw in assets.items():
        _need(type(raw) is bytes, "ASSET_NOT_BYTES")
        record = by_path[path]
        _need(len(raw) == record["size"] and _sha(raw) == record["sha256"], "ASSET_PIN_MISMATCH")
    for path, digest in profile["source_pins"].items():
        raw = sources[path]
        _need(type(raw) is bytes and _sha(raw) == digest, "SOURCE_PIN_MISMATCH")
    for path, pin in profile["asset_pins"].items():
        _need(path in by_path, "INDEPENDENT_ASSET_PIN_MISSING")
        record = by_path[path]
        _need(record["size"] == pin["size"] and record["sha256"] == pin["sha256"], "INDEPENDENT_ASSET_PIN_DRIFT")
    aggregate = "".join(f"{row['path']}\t{row['size']}\t{row['sha256']}\n" for row in manifest["files"]).encode("utf-8")
    digest = _sha(aggregate)
    _need(digest == manifest["payload_sha256"], "PAYLOAD_DIGEST_NOT_RECOMPUTABLE")
    total = sum(row["size"] for row in manifest["files"])
    nonfont = sum(row["size"] for row in manifest["files"] if not row["path"].endswith(".woff2"))
    _need(total == profile["expected_payload_bytes"], "PAYLOAD_BYTES_DRIFT")
    _need(nonfont == profile["expected_nonfont_bytes"], "NONFONT_BYTES_DRIFT")
    _need(total <= profile["max_payload_bytes"] and nonfont <= profile["max_nonfont_bytes"], "PAYLOAD_BUDGET_EXCEEDED")
    html = [name for name in by_path if name.endswith(".html")]
    _need(len(html) == profile["html_count"], "HTML_COUNT_DRIFT")
    _need("404.html" in html, "HTML_404_MISSING")
    expected_routes = accepted_routes(profile["guide_slugs"])
    derived_routes = [_route_for_asset(path) for path in html if path != "404.html"]
    _need(len(derived_routes) == len(set(derived_routes)), "DERIVED_ROUTE_DUPLICATE")
    _exact_urls(derived_routes, expected_routes, "HTML_ROUTE_PARITY")
    _exact_urls(public_routes, expected_routes, "PUBLIC_ROUTE_PARITY")
    canonical = frozenset(ORIGIN + route for route in expected_routes)
    _exact_urls(sitemap_urls, canonical, "SITEMAP_PARITY")
    _exact_urls(llms_urls, canonical, "LLMS_PARITY")
    # The supplied URL lists are NOT release authority. Independently parse the
    # exact sitemap/llms payload bytes whose SHA-256 is sealed by the manifest.
    _need("sitemap.xml" in assets and "llms.txt" in assets, "CRAWLER_ASSETS_MISSING")
    sitemap_raw = assets["sitemap.xml"]
    _need(b"<!DOCTYPE" not in sitemap_raw.upper() and b"<!ENTITY" not in sitemap_raw.upper(),
          "SITEMAP_DTD_DENIED")
    try:
        sitemap_tree = ET.fromstring(sitemap_raw)
        actual_sitemap = [node.text.strip() if node.text else ""
                          for node in sitemap_tree.findall(".//{*}url/{*}loc")]
    except (ET.ParseError, UnicodeError, ValueError) as err:
        raise AdmissionDenied("SITEMAP_XML_INVALID") from err
    _exact_urls(actual_sitemap, canonical, "SITEMAP_BYTES")
    try:
        llms_text = assets["llms.txt"].decode("utf-8")
    except UnicodeError as err:
        raise AdmissionDenied("LLMS_UTF8_INVALID") from err
    actual_llms = re.findall(r"\]\((https?://[^)\s]+)\)", llms_text)
    _exact_urls(actual_llms, canonical, "LLMS_BYTES")
    _check_guides(profile, assets)
    return ValidationReceipt(release_id, profile_sha, manifest_sha, digest, len(assets), len(expected_routes), len(html), len(profile["guide_slugs"]))


def validate_full(
    release_id: str, profile_bytes: bytes, manifest_bytes: bytes,
    assets: Mapping[str, bytes], sources: Mapping[str, bytes],
    public_routes: Sequence[str], sitemap_urls: Sequence[str], llms_urls: Sequence[str],
) -> ValidationReceipt:
    """Historical policy pins only; cannot self-approve unknown releases."""
    return _validate_under_test_trust(
        release_id, profile_bytes, manifest_bytes, assets, sources,
        public_routes, sitemap_urls, llms_urls,
        APPROVED_HISTORICAL_PINS, test_mode=False,
    )
