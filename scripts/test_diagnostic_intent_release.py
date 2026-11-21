"""Scope and integrity regressions for RU/EN static diagnostic intent."""
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
parent = release.verified_parent()
original = {r["path"]: r["sha256"] for r in parent["files"]}
for name in sorted(release.DONOR_PAGES):
    body = (release.LIVE / name).read_bytes()
    assert release.sha(release.restore_parent_link(name, body)) == original[name]

rejects("manifest digest", manifest_override=(release.LIVE / "_release.json").read_bytes() + b" ")
rejects("unknown file", file_overrides={"other.html": b""})
for name in ("index.html", "en/pricing.html", "en/method.html", "lead-form-runtime.js",
             "sitemap.xml", "analytics/preferences.js", "vercel.json"):
    rejects("static byte " + name, file_overrides={name: (release.LIVE / name).read_bytes() + b" "})
rejects("unknown source", source_overrides={"other.ts": b""})
for rel in ("lib/guides.ts", "components/LeadForm.tsx", "lib/diagnostic-intent.ts"):
    rejects("source " + rel, source_overrides={rel: b" "})
print(f"Diagnostic release verified: {manifest['file_count']} assets, 18 localized diagnostic links, 13 tamper fixtures")
