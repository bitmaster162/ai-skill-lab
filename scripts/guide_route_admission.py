#!/usr/bin/env python3
"""T1.5: explicit public-route admission, preserving the 52-route baseline.

Additional guide routes require a separately reviewed and approved slug here.
Never infer publishing authority from files found on disk or from a route count.
Consumers use the default allowlist; the override exists for in-memory tests.
"""
from __future__ import annotations

from pathlib import Path
from collections.abc import Iterable
import hashlib
import json
import re

ORIGIN = "https://aiskillab.work"
BASELINE_ROUTES = frozenset(
    """
/
/about
/build
/business
/certificate
/challenge
/curriculum
/en
/en/about
/en/build
/en/business
/en/certificate
/en/challenge
/en/curriculum
/en/family
/en/faq
/en/guides
/en/guides/ai-safety-for-kids
/en/kids
/en/matcher
/en/method
/en/parents
/en/personal
/en/phuket
/en/pricing
/en/privacy
/en/projects
/en/proof
/en/safety
/en/start
/en/studio
/en/teens
/en/terms
/family
/faq
/guides
/guides/ai-safety-for-kids
/kids
/matcher
/method
/parents
/personal
/phuket
/pricing
/privacy
/projects
/proof
/safety
/start
/studio
/teens
/terms
    """.split()
)
# Current owner approval is for the admission infrastructure only, not content.
# A later owner-approved content change must explicitly add its reviewed slug.
APPROVED_ADDITIONAL_GUIDE_SLUGS: frozenset[str] = frozenset()

if len(BASELINE_ROUTES) != 52:
    raise RuntimeError("T1.5 baseline route list is not exactly 52 unique routes")


class RouteAdmissionError(ValueError):
    """A public route has no explicit owner-approved admission."""


# Future release preparation is deliberately inert on E3.5 and unknown releases.
_FUTURE_GUIDE_RELEASE = "T1_6F2_ADULT_FIRST_TASKS_R1"
_FUTURE_GUIDE_SLUG = "ai-first-tasks-for-adults"
_FUTURE_GUIDE_PAYLOAD_SHA = "bd972c8b657e6ebf558da3630970668f935b149abc88e28e10cc53a36d9c5973"
_FUTURE_GUIDE_MD_SHA = {
    "ru": "5c5f8d8da100a8657aeefbe5d9044462095e92db341e240a37bdebae57bba61b",
    "en": "b0bcd0a6b545d2d8d4b190e55ab9d3c76350a9a30a8e1c745fb23e04b48df671",
}
_FUTURE_GUIDE_STATIC = {
    "guides/ai-first-tasks-for-adults.html": (27314, "f3cecb6ea3f46ab64ac3d3ab16db955ab8776d5edeb0c87b3b9b46bcaae2af91"),
    "en/guides/ai-first-tasks-for-adults.html": (20480, "dd43b529fac595d4ac5ea2d848de54db8dd11be761bf873b109593476f2c58aa"),
}


def _reviewed_future_guide_slugs() -> tuple[str, ...]:
    """Return zero or one admitted slugs; any missing or altered evidence denies."""
    root = Path(__file__).resolve().parents[1]
    try:
        manifest = json.loads((root / "deploy/live/_release.json").read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            return ()
        if (
            manifest.get("schema") != "ai-skill-lab.static-release.v1"
            or manifest.get("release_id") != _FUTURE_GUIDE_RELEASE
            or type(manifest.get("file_count")) is not int
            or manifest["file_count"] != 98
            or manifest.get("payload_sha256") != _FUTURE_GUIDE_PAYLOAD_SHA
        ):
            return ()
        files = manifest.get("files")
        if not isinstance(files, list) or len(files) != 98:
            return ()
        index: dict[str, tuple[int, str]] = {}
        for entry in files:
            if (
                not isinstance(entry, dict)
                or not isinstance(entry.get("path"), str)
                or type(entry.get("size")) is not int
                or not isinstance(entry.get("sha256"), str)
                or entry["path"] in index
            ):
                return ()
            index[entry["path"]] = entry["size"], entry["sha256"]
        if any(index.get(rel) != expected for rel, expected in _FUTURE_GUIDE_STATIC.items()):
            return ()
        for lang, digest in _FUTURE_GUIDE_MD_SHA.items():
            guide = root / "guides" / "aiskillab" / f"{_FUTURE_GUIDE_SLUG}.{lang}.md"
            if hashlib.sha256(guide.read_bytes()).hexdigest() != digest:
                return ()
    except (OSError, ValueError, UnicodeError, TypeError):
        return ()
    return (_FUTURE_GUIDE_SLUG,)


def admitted_routes(
    approved_slugs: Iterable[str] | None = None,
) -> frozenset[str]:
    """Return exact allowed paths; approved_slugs is for synthetic QA only."""
    slugs = (
        tuple(APPROVED_ADDITIONAL_GUIDE_SLUGS) + _reviewed_future_guide_slugs()
        if approved_slugs is None else tuple(approved_slugs)
    )
    if len(slugs) != len(set(slugs)):
        raise RouteAdmissionError("duplicate guide admission slug")
    routes = set(BASELINE_ROUTES)
    for slug in slugs:
        if not isinstance(slug, str) or not re.fullmatch(
            r"[a-z0-9]+(?:-[a-z0-9]+)*", slug
        ):
            raise RouteAdmissionError(f"invalid guide admission slug: {slug!r}")
        pair = {f"/guides/{slug}", f"/en/guides/{slug}"}
        if routes.intersection(pair):
            raise RouteAdmissionError(f"guide admission duplicates baseline: {slug}")
        routes.update(pair)
    return frozenset(routes)


def admitted_route_count(approved_slugs: Iterable[str] | None = None) -> int:
    return len(admitted_routes(approved_slugs))


def require_route_set(
    routes: Iterable[str],
    label: str = "public routes",
    *,
    approved_slugs: Iterable[str] | None = None,
) -> int:
    actual = tuple(routes)
    expected = admitted_routes(approved_slugs)
    if len(actual) != len(set(actual)):
        raise RouteAdmissionError(f"{label}: duplicate routes")
    missing, unexpected = expected.difference(actual), set(actual).difference(expected)
    if missing or unexpected:
        raise RouteAdmissionError(
            f"{label}: missing={sorted(missing)} unexpected={sorted(unexpected)}"
        )
    return len(expected)


def require_canonical_urls(
    urls: Iterable[str],
    label: str = "canonical URLs",
    *,
    approved_slugs: Iterable[str] | None = None,
) -> int:
    actual = tuple(urls)
    expected = {ORIGIN + path for path in admitted_routes(approved_slugs)}
    if len(actual) != len(set(actual)):
        raise RouteAdmissionError(f"{label}: duplicate URLs")
    missing, unexpected = expected.difference(actual), set(actual).difference(expected)
    if missing or unexpected:
        raise RouteAdmissionError(
            f"{label}: missing={sorted(missing)} unexpected={sorted(unexpected)}"
        )
    return len(expected)


def route_for_html(live: Path, path: Path) -> str:
    relative = path.relative_to(live).as_posix()
    if relative == "index.html":
        return "/"
    if relative == "en.html":
        return "/en"
    if relative == "404.html":
        raise RouteAdmissionError("404 must not be a public route")
    return "/" + relative.removesuffix(".html")


def require_public_html(live: Path) -> int:
    files = sorted(p for p in live.rglob("*.html") if p.name != "404.html")
    return require_route_set(
        (route_for_html(live, path) for path in files), "public static HTML"
    )
