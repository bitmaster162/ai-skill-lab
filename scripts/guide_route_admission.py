#!/usr/bin/env python3
"""T1.5: explicit public-route admission, preserving the 52-route baseline.

Additional guide routes require a separately reviewed and approved slug here.
Never infer publishing authority from files found on disk or from a route count.
Consumers use the default allowlist; the override exists for in-memory tests.
"""
from __future__ import annotations

from pathlib import Path
from collections.abc import Iterable
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


def admitted_routes(
    approved_slugs: Iterable[str] | None = None,
) -> frozenset[str]:
    """Return exact allowed paths; approved_slugs is for synthetic QA only."""
    slugs = (
        tuple(APPROVED_ADDITIONAL_GUIDE_SLUGS)
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
