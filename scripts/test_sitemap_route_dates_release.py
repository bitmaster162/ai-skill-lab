"""Exercise the sitemap successor and replay all frozen R2/R1 diagnostic fixtures."""
import subprocess
import sys

import diagnostic_intent_release as previous
import sitemap_route_dates_release as release


def rejects(reason, **inputs):
    try:
        release.verify(**inputs)
    except ValueError as exc:
        assert reason in str(exc), str(exc)
    else:
        raise AssertionError("Undetected sitemap release mutation: " + reason)


manifest = release.verify()
assert manifest["file_count"] == 112 and len(release.ROUTES) == 18
xml = (release.LIVE / "sitemap.xml").read_bytes()
rejects("manifest digest", manifest_override=(release.LIVE / "_release.json").read_bytes() + b" ")
# Neither a fabricated build-day date nor a rewritten URL can pass the exact diff.
for changed in (
    xml.replace(b"2026-11-21", b"2026-11-22", 1),
    xml.replace(b"2026-10-16", b"2026-11-21", 1),
    xml.replace(b"/en/teens</loc>", b"/en/other</loc>", 1),
):
    assert changed != xml
    rejects("sitemap delta", file_overrides={"sitemap.xml": changed})
rejects("static byte en/start.html", file_overrides={"en/start.html": b"changed"})
rejects("unknown file", file_overrides={"unexpected": b""})
for rel in ("app/sitemap.ts", "lib/guides.ts", "components/LeadForm.tsx"):
    rejects("source " + rel, source_overrides={rel: b"changed"})
files = ["deploy/live", "scripts/diagnostic_intent_release.py", "scripts/test_diagnostic_intent_release.py",
         previous.PARENT_VERIFIER, previous.PARENT_TEST, previous.parent.R3_VERIFIER, previous.parent.R3_TEST,
         *previous.SOURCE_SHA]
with previous.historical_workspace(release.PARENT_COMMIT, files) as workspace:
    subprocess.run([sys.executable, "-B", "scripts/test_diagnostic_intent_release.py"],
                   cwd=workspace, check=True)
print("Sitemap route dates verified: 18 changes, 111 unchanged assets, archived diagnostic R2 and R1.")
