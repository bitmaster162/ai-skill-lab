"""Scope and integrity regressions for RU/EN static diagnostic intent."""
import subprocess
import sys

import diagnostic_intent_release as release


def rejects(reason, **fixture):
    try:
        release.verify(**fixture)
    except ValueError as exc:
        assert reason in str(exc), str(exc)
    else:
        raise AssertionError("Undetected diagnostic release mutation: " + reason)


manifest = release.verify()
assert len(release.DONOR_PAGES) == 18
prior = release.verified_parent()
parent_rows = {row["path"]: row for row in prior["files"]}
changed = {row["path"] for row in manifest["files"] if row != parent_rows[row["path"]]}
assert changed == {"start.html", "en/start.html", "lead-form-runtime.js"}

# Re-run all original R1 fixtures against its own Git code, source pins and 112-file payload.
with release.diagnostic_r1_workspace() as workspace:
    subprocess.run([sys.executable, "-B", "scripts/test_diagnostic_intent_release.py"],
                   cwd=workspace, check=True)

rejects("manifest digest", manifest_override=(release.LIVE / "_release.json").read_bytes() + b" ")
rejects("unknown file", file_overrides={"other.html": b""})
for name in ("index.html", "en/pricing.html", "en/method.html", "lead-form-runtime.js",
             "sitemap.xml", "analytics/preferences.js", "vercel.json", "start.html", "en/start.html"):
    rejects("static byte " + name, file_overrides={name: (release.LIVE / name).read_bytes() + b" "})
rejects("unknown source", source_overrides={"other.ts": b""})
for rel in ("lib/guides.ts", "components/LeadForm.tsx", "lib/diagnostic-intent.ts", "public/lead-form-runtime.js",
            "components/workshop/WorkshopShell.tsx", "components/workshop/StartLanguageLink.tsx"):
    rejects("source " + rel, source_overrides={rel: b" "})
print(f"Diagnostic R2 verified: {manifest['file_count']} assets, three changed versus R1, archived R1 fixtures passed")
