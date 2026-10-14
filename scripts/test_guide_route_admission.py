#!/usr/bin/env python3
"""Read-only, in-memory route-admission acceptance fixtures for T1.5."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from guide_route_admission import (
    APPROVED_ADDITIONAL_GUIDE_SLUGS,
    BASELINE_ROUTES,
    ORIGIN,
    RouteAdmissionError,
    admitted_route_count,
    admitted_routes,
    require_canonical_urls,
    require_public_html,
    require_route_set,
)

LIVE = Path(__file__).resolve().parents[1] / "deploy" / "live"
SYNTHETIC = "fixture-second-guide"
PAIR = {f"/guides/{SYNTHETIC}", f"/en/guides/{SYNTHETIC}"}


FUTURE_RELEASE = "T1_6F2_ADULT_FIRST_TASKS_R1"
FUTURE_PAIR = frozenset({
    "/guides/ai-first-tasks-for-adults",
    "/en/guides/ai-first-tasks-for-adults",
})


def expected_live_routes() -> frozenset[str]:
    """Preserve 52 historical routes; require two SHA-admitted future routes."""
    release = json.loads((LIVE / "_release.json").read_text(encoding="utf-8")).get("release_id")
    if release == "PHUKET_UNIVERSE_U1_STATIC_R3_20261014":
        return BASELINE_ROUTES | FUTURE_PAIR | frozenset({"/phuket-universe", "/en/phuket-universe"})
    return BASELINE_ROUTES | FUTURE_PAIR if release == FUTURE_RELEASE else BASELINE_ROUTES


class RouteAdmissionTest(unittest.TestCase):
    def test_no_new_slug_has_release_authority(self) -> None:
        self.assertEqual(APPROVED_ADDITIONAL_GUIDE_SLUGS, frozenset())
        self.assertEqual(admitted_routes(), expected_live_routes())
        self.assertEqual(admitted_route_count(), len(expected_live_routes()))

    def test_52_baseline_exact(self) -> None:
        self.assertEqual(len(BASELINE_ROUTES), 52)
        self.assertEqual(require_route_set(sorted(BASELINE_ROUTES), approved_slugs=[]), 52)

    def test_existing_static_html(self) -> None:
        self.assertEqual(require_public_html(LIVE), len(expected_live_routes()))

    def test_existing_sitemap_exact(self) -> None:
        urls = re.findall(
            r"<loc>(https://[^<]+)</loc>",
            (LIVE / "sitemap.xml").read_text(encoding="utf-8"),
        )
        self.assertEqual(require_canonical_urls(urls), len(expected_live_routes()))

    def test_existing_llms_exact(self) -> None:
        urls = re.findall(
            r"\]\((https://[^)]+)\)",
            (LIVE / "llms.txt").read_text(encoding="utf-8"),
        )
        self.assertEqual(require_canonical_urls(urls), len(expected_live_routes()))

    def test_54_pair_explicitly_admitted(self) -> None:
        candidate = BASELINE_ROUTES | PAIR
        self.assertEqual(require_route_set(candidate, approved_slugs=[SYNTHETIC]), 54)
        self.assertEqual(
            require_canonical_urls(
                [ORIGIN + path for path in candidate],
                approved_slugs=[SYNTHETIC],
            ),
            54,
        )

    def test_53_single_locale_rejected(self) -> None:
        candidate = BASELINE_ROUTES | {f"/guides/{SYNTHETIC}"}
        with self.assertRaisesRegex(RouteAdmissionError, "missing="):
            require_route_set(candidate, approved_slugs=[SYNTHETIC])

    def test_54_unapproved_pair_rejected(self) -> None:
        with self.assertRaisesRegex(RouteAdmissionError, "unexpected="):
            require_route_set(BASELINE_ROUTES | PAIR)

    def test_54_wrong_slug_rejected(self) -> None:
        with self.assertRaises(RouteAdmissionError):
            require_route_set(
                BASELINE_ROUTES | PAIR, approved_slugs=["some-other-guide"]
            )

    def test_replacement_of_a_baseline_route_rejected(self) -> None:
        with self.assertRaises(RouteAdmissionError):
            require_route_set((BASELINE_ROUTES - {"/personal"}) | {"/altered"})

    def test_duplicate_route_rejected(self) -> None:
        with self.assertRaisesRegex(RouteAdmissionError, "duplicate"):
            require_route_set(list(BASELINE_ROUTES) + ["/personal"])

    def test_duplicate_sitemap_url_rejected(self) -> None:
        urls = [ORIGIN + route for route in BASELINE_ROUTES]
        with self.assertRaisesRegex(RouteAdmissionError, "duplicate"):
            require_canonical_urls(urls + [ORIGIN + "/personal"])

    def test_wrong_origin_rejected(self) -> None:
        urls = [ORIGIN + route for route in BASELINE_ROUTES]
        urls[0] = urls[0].replace(ORIGIN, "https://wrong.example")
        with self.assertRaises(RouteAdmissionError):
            require_canonical_urls(urls)

    def test_invalid_slug_rejected(self) -> None:
        for slug in ("../admin", "UPPER", "hello_world", "", "a--b"):
            with self.subTest(slug=slug), self.assertRaises(RouteAdmissionError):
                admitted_routes([slug])

    def test_baseline_slug_cannot_be_reapproved(self) -> None:
        with self.assertRaisesRegex(RouteAdmissionError, "duplicates baseline"):
            admitted_routes(["ai-safety-for-kids"])

    def test_duplicate_approval_rejected(self) -> None:
        with self.assertRaisesRegex(RouteAdmissionError, "duplicate guide"):
            admitted_routes([SYNTHETIC, SYNTHETIC])


if __name__ == "__main__":
    unittest.main(verbosity=2)
