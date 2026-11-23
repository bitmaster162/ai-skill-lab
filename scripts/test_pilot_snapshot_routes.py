"""Regression checks on a private copy of a sealed pilot site."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from guide_route_admission import BASELINE_ROUTES, RouteAdmissionError, admitted_routes, pilot_snapshot_routes

EXTRA = {
    prefix + route for prefix in ("", "/en") for route in (
        "/phuket-universe", "/guides/ai-first-tasks-for-adults",
        "/guides/ai-start-for-adults", "/guides/ai-pilot-for-small-business",
    )
}


def test_snapshot(source: Path) -> None:
    case = unittest.TestCase()
    with tempfile.TemporaryDirectory() as name:
        site = Path(name) / "site"
        shutil.copytree(source, site)
        case.assertEqual(pilot_snapshot_routes(site), BASELINE_ROUTES | EXTRA)
        case.assertEqual(admitted_routes(approved_slugs=()), BASELINE_ROUTES)

        manifest = site / "_release.json"
        original = manifest.read_bytes()
        manifest.write_bytes(original + b" ")
        with case.assertRaisesRegex(RouteAdmissionError, "manifest digest"):
            pilot_snapshot_routes(site)
        manifest.write_bytes(original)

        guide = site / "guides/ai-pilot-for-small-business.html"
        content = guide.read_bytes()
        guide.write_bytes(content + b" ")
        with case.assertRaisesRegex(RuntimeError, "Payload bytes"):
            pilot_snapshot_routes(site)
        guide.write_bytes(content)

        extra = site / "unreviewed.html"
        extra.write_text("unreviewed", encoding="utf-8")
        with case.assertRaisesRegex(RuntimeError, "Manifest count"):
            pilot_snapshot_routes(site)
        extra.unlink()
        extra.symlink_to(guide)
        with case.assertRaisesRegex(RouteAdmissionError, "symlink"):
            pilot_snapshot_routes(site)
        extra.unlink()

        spoof = json.loads(original)
        spoof["release_id"] += "_UNKNOWN"
        manifest.write_text(json.dumps(spoof), encoding="utf-8")
        case.assertIsNone(pilot_snapshot_routes(site))
